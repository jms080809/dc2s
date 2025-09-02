import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
import numpy as np
from moviepy import *

def generate_discord_chat_shorts(
    scenario: dict,
    title_font: str = "./asset/fonts/Orbit-Regular.ttf",
    message_font: str = "./asset/fonts/Orbit-Regular.ttf",
    watermark_font: str = "./asset/fonts/Orbit-Regular.ttf",
    filename: str = "output",
):
    """
    제공된 이미지 레이아웃에 맞춰 재구성된 YouTube Shorts 영상 생성 함수.
    """
    # --- 1. 영상 기본 설정 ---
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    FPS = 30
    BG_COLOR = (22, 23, 27)
    
    # 레이아웃 설정
    SIDE_PADDING = 100
    AVATAR_SIZE = 120  # 이미지를 참고하여 아바타 크기 조정
    # 💡 요소 사이의 수직 간격 정의
    AVATAR_USER_GAP = 30
    USER_MSG_GAP = 20
    ATTACHMENT_SIZE = 700

    # 폰트 크기
    TITLE_FONT_SIZE = 70
    MESSAGE_FONT_SIZE = 60
    USERNAME_FONT_SIZE = 50
    WATERMARK_FONT_SIZE = 40
    CAPTIONSIBAL = None
    
    DEFAULT_SOUND_PATH = "./asset/sounds/discord-notification.mp3"

    # --- 2. 헬퍼 함수 ---
    def normalize_audio(audio_clip:AudioClip, target_db=-1.0)->AudioClip:
        """오디오 클립을 지정된 dB 피크 레벨로 평준화(리미터처럼 사용)합니다."""
        target_amplitude = 10**(target_db / 20.0)
        current_max_amplitude = audio_clip.max_volume()
        if current_max_amplitude == 0:
            return audio_clip
        factor = target_amplitude / current_max_amplitude
        return audio_clip.with_volume_scaled(factor)
    def make_attachment_image(url:str) -> ImageClip:
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            attachment_img = Image.open(img_data).convert("RGBA")
            attachment_img = ImageOps.fit(attachment_img, (ATTACHMENT_SIZE, ATTACHMENT_SIZE), Image.Resampling.LANCZOS)
                        
            return ImageClip(np.array(attachment_img))
        except Exception as e:
            print(f"❌ attachment processing error: {url}, {e}")
            return ColorClip(size=(ATTACHMENT_SIZE, ATTACHMENT_SIZE), color=(0,0,0,0))

    def make_circle_image(url: str) -> ImageClip:
        """URL 이미지를 원형으로 마스킹하여 ImageClip으로 반환합니다."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            avatar_img = Image.open(img_data).convert("RGBA")
            avatar_img = ImageOps.fit(avatar_img, (AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
            
            avatar_img.putalpha(mask)
            return ImageClip(np.array(avatar_img))
        except Exception as e:
            print(f"❌ 아바타 처리 오류: {url}, {e}")
            return ColorClip(size=(AVATAR_SIZE, AVATAR_SIZE), color=(0,0,0,0))

    def create_message_scene(msg_data: dict, chatters: dict) -> CompositeVideoClip:
        """하나의 메시지 데이터를 이미지 레이아웃에 맞는 장면으로 변환합니다."""
        duration = msg_data.get("duration", 2)
        username = msg_data["username"]
        attachment_src = ""
        scene_elements = []

        # 1. 아바타 클립 생성
        avatar_url = chatters.get(username, {}).get("avatarURL")
        avatar_clip = make_circle_image(avatar_url) if avatar_url else \
                      ColorClip(size=(AVATAR_SIZE, AVATAR_SIZE), color=(0,0,0,0))
        
        # 2. 텍스트 클립 생성
        username_line_text = f'{username}'
        text_width = VIDEO_WIDTH - SIDE_PADDING * 2
        
        username_line_clip = TextClip(
            text=username_line_text,
            font_size=USERNAME_FONT_SIZE, font=message_font, color="lightgray",
            size=(text_width, USERNAME_FONT_SIZE*2), method="caption", text_align="center"
        )
        
        content_clip = TextClip(
            text=msg_data["content"],
            font_size=MESSAGE_FONT_SIZE, font=message_font, color="white",
            size=(text_width, MESSAGE_FONT_SIZE*4), method="caption", text_align="center"
        )
        
        # 3. 💡 이미지 레이아웃에 맞게 위치 재계산
        # 전체 콘텐츠 블록의 높이를 계산
        total_content_height = (avatar_clip.h + AVATAR_USER_GAP + 
                                username_line_clip.h + USER_MSG_GAP + 
                                content_clip.h)
        
        # 콘텐츠 블록이 시작될 Y좌표 계산 (화면 중앙 정렬)
        start_y = (VIDEO_HEIGHT - total_content_height) / 2
        
        # 각 요소를 순서대로 중앙에 배치
        avatar_y = start_y
        username_y = avatar_y + avatar_clip.h + AVATAR_USER_GAP
        content_y = username_y + username_line_clip.h + USER_MSG_GAP
        
        avatar_clip = avatar_clip.with_duration(duration).with_position(("center", avatar_y))
        username_line_clip = username_line_clip.with_duration(duration).with_position(("center", username_y))
        content_clip = content_clip.with_duration(duration).with_position(("center", content_y))
        #attachment replacement
        try:
            if len(msg_data["attachments"])!=0:
                attachment_src=msg_data["attachments"][0]["url"]
                content_clip = make_attachment_image(attachment_src) or ColorClip(size=(ATTACHMENT_SIZE,ATTACHMENT_SIZE),color=(0,0,0,0))
                content_clip = content_clip.with_position("center").with_duration(duration)
        except Exception as e:
            print(e)
            pass

        scene_elements.extend([avatar_clip, username_line_clip, content_clip])

        scene = CompositeVideoClip(scene_elements, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        
        # 4. 사운드 처리
        sound_path = msg_data.get("sound", DEFAULT_SOUND_PATH)
        if os.path.exists(sound_path):
            try:
                #if the sfx not in duration, sped up
                audio = AudioFileClip(sound_path)
                if audio.duration > duration:
                    audio=audio.with_speed_scaled(duration/audio.duration,duration)
                    audio= normalize_audio(audio, target_db=-3.0)
                scene = scene.with_audio(audio)
            except Exception as e:
                print(f"❌ 사운드 처리 실패: {sound_path}, {e}")
        else:
            print(f"⚠️ 경고: 사운드 파일을 찾을 수 없습니다 - {sound_path}")
        return scene

    # --- 3. 메인 로직 ---
    chatters_info = scenario.get("chatters", {})
    message_clips = [create_message_scene(msg, chatters_info) for msg in scenario.get("contents", [])]

    if not message_clips:
        print("생성할 메시지가 없습니다.")
        return

    chat_sequence = concatenate_videoclips(message_clips, method="compose")
    total_duration = chat_sequence.duration

    overlays = []
    descriptions = scenario.get("descriptions", {})
    if descriptions.get("title"):
        title_clip = (TextClip(
                text=descriptions["title"], font_size=TITLE_FONT_SIZE, font=title_font, color="white",
                size=(VIDEO_WIDTH - SIDE_PADDING*2, TITLE_FONT_SIZE*2), method="caption"
            )
            .with_duration(total_duration)
            .with_position(("center", 150)) # 제목 위치 조정
        )
        overlays.append(title_clip)

    if descriptions.get("watermark"):
        watermark_clip = (TextClip(
                text=descriptions["watermark"], font_size=WATERMARK_FONT_SIZE, font=watermark_font, color="gray",
                size=(VIDEO_WIDTH - SIDE_PADDING*2, WATERMARK_FONT_SIZE*2), method="caption"
            )
            .with_duration(total_duration)
            .with_position(("center", VIDEO_HEIGHT - 150)) # 워터마크 위치 조정
        )
        overlays.append(watermark_clip)
        
    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=BG_COLOR).with_duration(total_duration)
    final_video = CompositeVideoClip([background, chat_sequence] + overlays).with_fps(FPS)

    # --- 4. 파일 출력 ---
    try:
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{filename}.mp4")
        
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="libmp3lame",
            threads=4,
            preset="ultrafast",
        )
        print(f"✅ 영상 생성 완료: {output_path}")
    except Exception as e:
        print(f"❌ 영상 파일 생성 중 오류가 발생했습니다: {e}")
