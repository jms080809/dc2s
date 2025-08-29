from openai import OpenAI
import json
import os
import utils
from datetime import datetime as dt
from dotenv import load_dotenv


@utils.debug_print
def genearte_scenario(content, save: bool, filename: str, translate: bool = False):
    load_dotenv("../env")
    sound_dir = "./asset/sounds"
    effect_list = []
    animation_list = []
    sound_prompt_list = " | ".join(
        [f'"{os.path.join(root, f)}"' for root, dirs, files in os.walk(sound_dir) for f in files if not f.endswith(".Identifier")]
    )
    prompt = f"""
    You are a data transformation expert. Convert a JSON chat log into a single, valid JSON object containing three keys: "descriptions", "chatters", and "contents".

    Requirements:

    1. "descriptions" object:
    - "title": generate from the chat content,which is not only concise but also funny like youtube video shorts,following informal language.
    language of this also follows 'translate' bool values.
    you have to write this like reddit users or 4chan users, and you have to write less than 11 words in korean. similarily,
    you also have to keep that length to other languages.
    you can include special characters and emojis if you want, and these are examples:
    선1정적인 남1자, 씨1봉방거;;;@@, 남1대문은 쉽게 닫을 수 없지ㅋ. 
    - "watermark": always "@h03_txle/tokkiyeah".

    2. "chatters" object:
    - Each unique username is a key.
    - Each value must be an object with only one key: "avatarURL".
    - Do not repeat avatar URLs in messages.

    3. "contents" array:
    - Each element must include:
        - "username"
        - "content" (If content is considered that it has dangerous information such as someone's real name, phone number, etc, you have to shade it )
        for example, 김정환 -> 김XX, 후선 -> XX, but you dont have to shade celebrity's or pseudo one. for example, Vladimir Putin, 김정은(Jeong un Kim), Donald Trump, 
        or Hoshou Marine, etc.
        - "timestamp"
        - "attachments" (if present, include the first with "url" and "media_type")
        - "sound" (from {sound_prompt_list}, default: "{sound_dir}/discord-notification.mp3")
        - "effect" (from {effect_list})
        - "animation" (from {animation_list}, with rules below),
        - "duration" 

    Animation rules:
    - Attachment present → "scaleFade"
    - Short messages (<20 chars) → "pop"
    - Long messages → "slideUp"
    - System/bot messages → "none"

    Sound rules:
    - Match sentiment/context to a provided sound if possible.
    - Otherwise use "{sound_dir}/discord-notification.mp3".

    Duration rules:

    Short messages (<20 chars) → 1–1.5 seconds

    Medium messages → 2–2.5 seconds

    Long messages (>50 chars) → 3–3.5 seconds

System/bot messages → 1 second
    Language rules:
    - You will receive a variable "translate".
        - If translate = false, keep all content text in the original language it was written in.
        - If translate = true, translate all content into the specified language.
    - Apply this consistently to message contents, titles, and any descriptive text.

    Output Format:
    - Must be a valid JSON object.
    - Top-level keys: "descriptions", "chatters", "contents".
    - All keys must use double quotes.
    - Do not include explanations, markdown, comments, or extra text.
    - Output JSON only. Never include ```json or ``` markers.
    """

    # ai-generation part
    OPENROUTERTOKEN = os.getenv("OPENROUTERTOKEN")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTERTOKEN,
    )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": str(content)},
        {"role": "user", "content": f"tranlsate={translate}"},
    ]
    completion = client.chat.completions.create(
        model="z-ai/glm-4.5-air:free",
        messages=messages,
    )
    print(
        f"""
        ======AI RAW DATA======
        {completion.choices[0].message.content}
        =======================
        """
    )
    output = json.loads(completion.choices[0].message.content)
    if save:
        file_src = f"./scenarios/{filename}_{dt.now().strftime('%y%m%d-%H%M%S')}.json"
        if os.path.isfile(file_src):
            os.remove(file_src)
        with open(file_src, "+a", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False, indent=2))
    return output
