import os
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from moviepy import (
    VideoClip,
    TextClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
import utils


@utils.debug_print
def generate_discord_chat_shorts(
    scenario: dict,
    title_font: str = "./asset/fonts/Orbit-Regular.ttf",
    message_font: str = "./asset/fonts/Orbit-Regular.ttf",
    watermark_font: str = "./asset/fonts/Orbit-Regular.ttf",
    filename: str = "output",
):
    """
    JSON 시나리오를 기반으로 유튜브 쇼츠 영상을 생성하는 함수.
    중앙 채팅이 가려지지 않도록 위/아래 여백을 확장하여 제목과 워터마크를 배치합니다.
    """
    # --- 1. 영상 기본 설정 ---
    VIDEO_WIDTH = 1080
    CHAT_HEIGHT = 1600  # 채팅 표시 영역
    TOP_MARGIN = 150
    BOTTOM_MARGIN = 120
    VIDEO_HEIGHT = CHAT_HEIGHT + TOP_MARGIN + BOTTOM_MARGIN

    FPS = 30
    BG_COLOR = (0, 0, 0)
    PADDING = 100

    TITLE_FONT_SIZE = 70
    MESSAGE_FONT_SIZE = 60
    USERNAME_FONT_SIZE = 50
    WATERMARK_FONT_SIZE = 40

    DEFAULT_SOUND_PATH = "./asset/sounds/discord-notification.mp3"

    YY = 300

    # --- 2. 헬퍼 함수 ---
    def apply_animation(clip: VideoClip, animation_type: str) -> VideoClip:
        return clip  # 확장 가능

    def create_message_scene(msg_data: dict) -> CompositeVideoClip:
        """하나의 메시지를 장면으로 변환"""
        duration = msg_data.get("duration", 2)
        animation = msg_data.get("animation", "none")

        scene_elements = []

        # 사용자 이름 클립 생성
        username_clip_base = TextClip(
            text=msg_data["username"],
            font_size=USERNAME_FONT_SIZE,
            font=message_font,
            color="gray",
            size=(VIDEO_WIDTH - PADDING, YY-100),
            method="label",
        )

        # 메시지 내용 클립 생성
        content_clip_base = TextClip(
            text=msg_data["content"],
            font_size=MESSAGE_FONT_SIZE,
            font=message_font,
            color="white",
            size=(VIDEO_WIDTH - PADDING, YY),
            method="label",
        )

        # 전체 텍스트 블록의 높이를 계산하고 중앙 정렬을 위한 y 좌표 계산
        total_text_height = username_clip_base.h + content_clip_base.h + 15  # 15px 간격
        start_y = (TOP_MARGIN + CHAT_HEIGHT / 2) - (total_text_height / 2)

        # 각 클립에 최종 위치와 기간 설정
        username_clip = username_clip_base.with_duration(duration).with_position(("center", start_y))

        content_y = start_y + username_clip_base.h + 15
        content_clip = content_clip_base.with_duration(duration).with_position(("center", content_y))

        scene_elements.append(username_clip)
        scene_elements.append(content_clip)

        # 첨부 이미지
        attachments = msg_data.get("attachments", [])
        if attachments and "url" in attachments[0]:
            try:
                response = requests.get(attachments[0]["url"])
                response.raise_for_status()
                pil_img = Image.open(BytesIO(response.content)).convert("RGBA")

                img_clip = (
                    ImageClip(np.array(pil_img))
                    .with_duration(duration)
                    .resize(width=VIDEO_WIDTH - PADDING)
                    .with_position(("center", content_clip.pos(0)[1] + content_clip.h + 20))
                )
                scene_elements.append(img_clip)
            except Exception as e:
                print(f"이미지 처리 오류: {e}")

        # 합성
        # 각 장면에 투명 배경을 추가하여 이전 장면이 가려지지 않도록 함
        transparent_bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration).with_opacity(0)
        message_visual_clip = CompositeVideoClip([transparent_bg] + scene_elements, size=(VIDEO_WIDTH, VIDEO_HEIGHT))

        # 오디오
        sound_path = msg_data.get("sound", DEFAULT_SOUND_PATH)
        final_clip_with_sound = message_visual_clip
        if os.path.exists(sound_path):
            try:
                audio_clip = AudioFileClip(sound_path)
                if audio_clip.duration > duration:
                    audio_clip = audio_clip.with_speed_scaled(final_duration=duration)
                final_clip_with_sound = message_visual_clip.with_audio(audio_clip)
            except Exception as e:
                print(f"사운드 처리 실패: {e}")
        else:
            print(f"경고: 사운드 파일 없음 - {sound_path}")

        return apply_animation(final_clip_with_sound, animation)

    # --- 3. 메인 로직 ---
    message_clips = [create_message_scene(msg) for msg in scenario.get("contents", [])]
    if not message_clips:
        print("생성할 메시지가 없습니다.")
        return

    chat_sequence = concatenate_videoclips(message_clips, method="compose")
    total_duration = chat_sequence.duration

    overlays = []
    descriptions = scenario.get("descriptions", {})

    # 제목
    if descriptions.get("title"):
        title_clip = (
            TextClip(
                text=descriptions["title"],
                font_size=TITLE_FONT_SIZE,
                font=title_font,
                color="white",
                size=(VIDEO_WIDTH - PADDING, YY),
                method="label",
            )
            .with_duration(total_duration)
            .with_position(("center", 40))  # TOP_MARGIN 안쪽
        )
        overlays.append(title_clip)

    # 워터마크
    if descriptions.get("watermark"):
        watermark_clip = (
            TextClip(
                text=descriptions["watermark"],
                font_size=WATERMARK_FONT_SIZE,
                font=watermark_font,
                color="gray",
                size=(VIDEO_WIDTH - PADDING, YY),
                method="label",
            )
            .with_duration(total_duration)
            .with_position(("center", VIDEO_HEIGHT - BOTTOM_MARGIN + 20))
        )
        overlays.append(watermark_clip)

    # 배경 + 합성
    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=BG_COLOR).with_duration(total_duration)
    final_video = CompositeVideoClip([background, chat_sequence] + overlays)
    final_video = final_video.with_fps(FPS)

    try:
        filename = f"./output/{filename}.mp4"
        final_video.write_videofile(
            filename,
            codec="libx264",
            audio_codec="libmp3lame",  # 소리 정상 출력
            threads=4,
            preset="medium",
        )
        print(f"✅ 영상 생성 완료: {filename}")
    except Exception as e:
        print(f"❌ 출력 오류: {e}")


# # --- 실행 예시 ---
# ex_scenario = {
#     "descriptions": {"title": "디지털 게이들의 밤샘 대화", "watermark": "@h03_txle/tokkiyeah"},
#     "contents": [
#         {"username": "퍼리보는사나이", "content": "디게이", "sound": "./asset/sounds/discord-notification.mp3", "duration": 2},
#         {"username": "ho3_txle", "content": "디지털 게이야", "sound": "./asset/sounds/discord-notification.mp3", "duration": 2},
#         {"username": "퍼리보는사나이", "content": ";;", "sound": "./asset/sounds/ack.mp3", "duration": 1},
#         {"username": "ho3_txle", "content": "후선짱 후욱후욱", "sound": "./asset/sounds/discord-notification.mp3", "duration": 2},
#     ],
# }

# generate_discord_chat_shorts(ex_scenario, output_file="discord_chat_video.mp4")
