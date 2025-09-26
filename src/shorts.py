from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
import numpy as np
from moviepy import *
import re, tempfile, os, requests


def generate_discord_chat_shorts(
    scenario: dict,
    title_font: str = "./asset/fonts/Orbit-Regular.ttf",
    message_font: str = "./asset/fonts/Orbit-Regular.ttf",
    watermark_font: str = "./asset/fonts/Orbit-Regular.ttf",
    filename: str = "output",
):
    """
    Generate a YouTube Shorts-style video that simulates Discord chat.
    """
    # --- 1. Video settings ---
    VIDEO_WIDTH, VIDEO_HEIGHT = 1080, 1920
    FPS = 30
    BG_COLOR = (22, 23, 27)

    # Layout settings
    SIDE_PADDING = 100
    AVATAR_SIZE = 250
    AVATAR_USER_GAP, USER_MSG_GAP = 30, 20
    ATTACHMENT_SIZE = 800

    # Font sizes
    TITLE_FONT_SIZE, MESSAGE_FONT_SIZE = 70, 60
    USERNAME_FONT_SIZE, WATERMARK_FONT_SIZE = 50, 40

    DEFAULT_SOUND_PATH = "./asset/sounds/discord-notification.mp3"

    # --- 2. Helper functions ---
    def make_circle_image(url: str) -> ImageClip:
        """Download image and mask it to a circle as ImageClip."""
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
            print(f"❌ Avatar image error: {url}, {e}")
            return ColorClip(size=(AVATAR_SIZE, AVATAR_SIZE), color=(0, 0, 0, 0))

    def normalize_audio(audio_clip: AudioClip, target_db=-1.0) -> AudioClip:
        """Normalize audio clip to a target dB peak level."""
        target_amplitude = 10 ** (target_db / 20.0)
        current_max = audio_clip.max_volume()
        if current_max == 0:
            return audio_clip
        factor = target_amplitude / current_max
        return audio_clip.with_volume_scaled(factor)

    def make_attachment_image(url: str) -> ImageClip:
        """Download and resize an image attachment."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            attachment_img = Image.open(img_data).convert("RGBA")
            attachment_img.thumbnail((ATTACHMENT_SIZE, ATTACHMENT_SIZE), Image.Resampling.LANCZOS)
            return ImageClip(np.array(attachment_img))
        except Exception as e:
            print(f"❌ Attachment image error: {url}, {e}")
            return ColorClip(size=(ATTACHMENT_SIZE, ATTACHMENT_SIZE), color=(0, 0, 0, 0))

    def make_attachment_gif(url: str) -> VideoFileClip:
        """Download and convert a gif attachment into VideoFileClip."""
        try:
            response = requests.get(url)
            response.raise_for_status()

            # If tenor view link, extract raw gif
            if url.startswith("https://tenor.com"):
                matches = re.findall(r'https://media1\.tenor\.com/[^\s"\']+\.gif', response.text)
                if not matches:
                    raise Exception("GIF URL not found")
                url = matches[0]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmp:
                tmp.write(requests.get(url).content)
                tmp_path = tmp.name

            clip = VideoFileClip(tmp_path)
            os.remove(tmp_path)
            clip = clip.resized(height=ATTACHMENT_SIZE, width=ATTACHMENT_SIZE)
            return clip

        except Exception as e:
            print(f"❌ Attachment gif error: {url}, {e}")
            raise e

    def create_message_scene(msg_data: dict, chatters: dict) -> CompositeVideoClip:
        """Convert one message into a video scene."""
        duration = msg_data.get("duration", 2)
        username = msg_data["username"]
        scene_elements = []

        # Avatar
        avatar_url = chatters.get(username, {}).get("avatarURL")
        avatar_clip = make_circle_image(avatar_url) if avatar_url else ColorClip(
            size=(AVATAR_SIZE, AVATAR_SIZE), color=(0, 0, 0, 0)
        )

        # Text
        text_width = VIDEO_WIDTH - SIDE_PADDING * 2
        username_clip = TextClip(
            text=username,
            font_size=USERNAME_FONT_SIZE, font=message_font, color="lightgray",
            size=(text_width, USERNAME_FONT_SIZE * 2), method="caption", text_align="center"
        )
        content_clip = TextClip(
            text=msg_data["content"],
            font_size=MESSAGE_FONT_SIZE, font=message_font, color="white",
            size=(text_width, MESSAGE_FONT_SIZE * 4), method="caption", text_align="center"
        )

        # Vertical layout
        total_height = avatar_clip.h + AVATAR_USER_GAP + username_clip.h + USER_MSG_GAP + content_clip.h
        start_y = (VIDEO_HEIGHT - total_height) / 2

        avatar_y, username_y, content_y = start_y, start_y + avatar_clip.h + AVATAR_USER_GAP, start_y + avatar_clip.h + AVATAR_USER_GAP + username_clip.h + USER_MSG_GAP

        avatar_clip = avatar_clip.with_duration(duration).with_position(("center", avatar_y))
        username_clip = username_clip.with_duration(duration).with_position(("center", username_y))
        content_clip = content_clip.with_duration(duration).with_position(("center", content_y))

        # Attachments
        try:
            if bool(msg_data.get("attachments")):
                attachment = msg_data["attachments"][0]
                if attachment["content_type"] == "gif":
                    content_clip = make_attachment_gif(attachment["url"])
                    duration = content_clip.duration
                elif attachment["content_type"] == "image":
                    content_clip = make_attachment_image(attachment["url"])
                content_clip = content_clip.with_position("center").with_duration(duration)
        except Exception as e:
            raise e

        scene_elements.extend([avatar_clip, username_clip, content_clip])
        scene = CompositeVideoClip(scene_elements, size=(VIDEO_WIDTH, VIDEO_HEIGHT))

        # Audio
        sound_path = msg_data.get("sound", DEFAULT_SOUND_PATH)
        if os.path.exists(sound_path):
            try:
                audio = AudioFileClip(sound_path)
                if audio.duration > duration:
                    audio = audio.with_speed_scaled(duration / audio.duration, duration)
                    audio = normalize_audio(audio, target_db=-3.0)
                scene = scene.with_audio(audio)
            except Exception as e:
                print(f"❌ Sound error: {sound_path}, {e}")
        else:
            print(f"⚠️ Warning: Sound file not found - {sound_path}")

        return scene

    # --- 3. Main logic ---
    chatters_info = scenario.get("chatters", {})
    message_clips = [create_message_scene(msg, chatters_info) for msg in scenario.get("contents", [])]

    if not message_clips:
        print("No messages to generate.")
        return

    chat_sequence = concatenate_videoclips(message_clips, method="compose")
    total_duration = chat_sequence.duration

    overlays = []
    descriptions = scenario.get("descriptions", {})
    if descriptions.get("title"):
        overlays.append(
            TextClip(
                text=descriptions["title"], font_size=TITLE_FONT_SIZE, font=title_font, color="white",
                size=(VIDEO_WIDTH - SIDE_PADDING * 2, TITLE_FONT_SIZE * 2), method="caption"
            ).with_duration(total_duration).with_position(("center", 150))
        )
    if descriptions.get("watermark"):
        overlays.append(
            TextClip(
                text=descriptions["watermark"], font_size=WATERMARK_FONT_SIZE, font=watermark_font, color="gray",
                size=(VIDEO_WIDTH - SIDE_PADDING * 2, WATERMARK_FONT_SIZE * 2), method="caption"
            ).with_duration(total_duration).with_position(("center", VIDEO_HEIGHT - 150))
        )

    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=BG_COLOR).with_duration(total_duration)
    final_video = CompositeVideoClip([background, chat_sequence] + overlays).with_fps(FPS)

    # --- 4. Export ---
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
        print(f"✅ Video generated successfully: {output_path}")
    except Exception as e:
        print(f"❌ Video export error: {e}")
