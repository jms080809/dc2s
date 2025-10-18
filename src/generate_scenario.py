from openai import OpenAI
import json
import os
import utils
from datetime import datetime as dt
from dotenv import load_dotenv
import unicodedata
@utils.debug_print
def generate_scenario(content, save: bool, filename: str, translate: bool = False):
    #ai resource loading part
    load_dotenv("../.env")

    sound_dir = "./asset/sounds"
    bgm_dir = "./asset/bgms"

    effect_list = []
    animation_list = []

    sound_prompt_list = [unicodedata.normalize("NFC", f) for _, _, files in os.walk(sound_dir) for f in files if f.lower().endswith((".mp3", ".wav", ".ogg"))]
    bgm_prompt_list = [unicodedata.normalize("NFC", f) for _, _, files in os.walk(bgm_dir) for f in files if f.lower().endswith((".mp3", ".wav", ".ogg"))]

    # 파일명만 넣도록 수정 (태그 제거)
    sound_prompt_list = ",".join(filename for filename in sound_prompt_list)
    bgm_prompt_list = ",".join(filename for filename in bgm_prompt_list)
    prompt = f"""
    [Role]
    You are a highly precise data transformation engine. Your sole function is to convert a raw chat log into a single-line, valid JSON object according to the strict rules and data sources provided below. You MUST NOT invent, guess, or hallucinate any filenames. You must only use filenames explicitly listed in [AvailableBGM] and [AvailableSounds]. Do not deviate from instructions.

    [DataSources]
        [AvailableBGM]
        {bgm_prompt_list}

        [AvailableSounds]
        {sound_prompt_list}

        [AvailableEffects]
        {effect_list}

        [AvailableAnimations]
        {animation_list}

    [TransformationRules]
    1. Top-Level JSON: Exactly three keys: "descriptions", "chatters", "contents".

    2. "descriptions":
        - "title": Funny/informal (<11 Korean chars or <15 English chars), follow 'translate' boolean.
        - "watermark": "@ho3_txle/tokkiyeah"
        - "bgm": MUST be selected from [AvailableBGM]. Format: "{bgm_dir}/{{filename}}". NEVER invent.

    3. "chatters":
        - Keys = unique usernames
        - Values = {{"avatarURL": ...}}, no duplicate URLs

    4. "contents" Array:
        - Each object = one chat message or attachment
        - **Attachment Splitting**: If text + attachment, split into 2 objects
        - Fields:
            - "username"
            - "content": Mask private info (김정환 → 김XX), profanity (씨발 → C발)
            - "sound": MUST be chosen from [AvailableSounds]. Format: "{sound_dir}/{{filename}}". If not found, fallback to "discord-notification.mp3". DO NOT invent.
            - "animation": Attachment → "scaleFade", text<20 → "pop", text>50 → "slideUp", system/bot → "none"
            - "duration": text<20 → 1.0–1.5, 20–50 → 2.0–2.5, >50 → 3.0–3.5, system/bot → 1.0
        - Language: If translate=True, translate all user text and title; else keep original.

    5. Special Rule:
        - NEVER output ` or invent any filenames

    [Example_AttachmentSplitting]
    # Input message contains both text and attachment
    # Input: {{ "username": "user1", "content": "Hello! https://example.com/image.gif", "timestamp": "25. 8. 18. PM 10:18" }}
    # Output:
    {{
        "username": "user1",
        "content": "Hello!",
        "timestamp": "25. 8. 18. PM 10:18",
        "attachments": [],
        "sound": "{sound_dir}/discord-notification.mp3",
        "effect": "none",
        "animation": "pop",
        "duration": 1.5
    }},
    {{
        "username": "user1",
        "content": "",
        "timestamp": "25. 8. 18. PM 10:18",
        "attachments": [{{ "url": "https://example.com/image.gif", "content_type": "gif" }}],
        "sound": "{sound_dir}/obiwan_says_hello_there.mp3",
        "effect": "none",
        "animation": "scaleFade",
        "duration": 2.0
    }}
    # All "sound" MUST be chosen EXACTLY from [AvailableSounds]. DO NOT invent or alter filenames.
    # 'content_type' MUST be either "gif" or "image", not MIME type. Tenor links are always "gif".

    [FinalCheck]
    - Every "bgm" and "sound" MUST exist EXACTLY in [AvailableBGM] or [AvailableSounds].
    - If a sound is missing, fallback to "discord-notification.mp3".
    - Attachment splitting must be applied correctly.
    - At least ⌊N/3⌋ different sound files used for N messages whenever possible.
    - NEVER invent filenames.
    - Map attachment MIME types (image/gif, image/jpeg, etc.) to "gif" or "image".

    [OutputSpecification]
    1. Output MUST be a single continuous line of valid JSON.
    2. Output MUST contain ONLY the JSON object.
    3. DO NOT add explanations, comments, or code fences.
    4. All "sound" values MUST be from [AvailableSounds] only. NEVER invent filenames.
    """


    # ai-generation part
    OPENROUTERTOKEN:str = os.getenv("OPENROUTERTOKEN")
    OPENROUTER_MODEL:str = os.getenv("OPENROUTER_MODEL")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTERTOKEN,
    )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": str(content)},
        {"role": "user", "content": f"tranlsate={translate}"},
    ]

    completion=""
    output=""
    tried=0
    #error handling for AI.. fuck
    for _ in range(3):
        try:
            completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages)
            print(f"""
            ======AI RAW DATA======
            {completion.choices[0].message.content}
            =======================
            """,flush=True)
            output = json.loads(completion.choices[0].message.content.strip(" "))
            break
        except Exception as e:
            tried+=1
            if tried==3:
                raise 
            continue
    #남겨두세요 만일을 위해 ^^
    if save:
        file_src = f"./scenarios/{filename}_{dt.now().strftime('%y%m%d-%H%M%S')}.json"
        if os.path.isfile(file_src):
            os.remove(file_src)
        if not os.path.exists(file_src):
              os.makedirs(os.path.dirname("./scenarios/"), exist_ok=True)
        with open(file_src, "+a", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False, indent=2))

    return output