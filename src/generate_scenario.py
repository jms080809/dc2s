from openai import OpenAI
import json
import os
import utils
from datetime import datetime as dt
from dotenv import load_dotenv


@utils.debug_print
def generate_scenario(content, save: bool, filename: str, translate: bool = False):
    load_dotenv("../env")
    sound_dir = "./asset/sounds"
    effect_list = []
    animation_list = []
    sound_prompt_list = " | ".join(
        [f'"{os.path.join(root, f)}"' for root, dirs, files in os.walk(sound_dir) for f in files if not f.endswith(".Identifier")]
    )
    prompt = f"""
    You are a data transformation expert. Convert a JSON chat log into a valid JSON object with keys: "descriptions", "chatters", "contents".

    1. "descriptions":
    - "title": funny titles, concise (<11 characters in korean, less than 15 characters in english), informal (Reddit/4chan style), follows 'translate' bool
    - "watermark": "@ho3_txle/tokkiyeah".

    2. "chatters":
    - Unique usernames as keys.
    - Values: object with "avatarURL" key only, no duplicate URLs.

    3. "contents" array:
    - Each item: "username", "content" (mask private info like 김정환→김XX, exclude celebrities), "timestamp", "attachments" (first with "url", "media_type"), "sound" (from {sound_prompt_list}, default: "{sound_dir}/discord-notification.mp3"), "effect" (from {effect_list}), "animation" (from {animation_list}), "duration".

    Rules:
    - Animation: Attachment → "scaleFade", <20 chars → "pop", >50 chars → "slideUp", system/bot → "none".
    - Sound: you have to choose appropriate sounds according to chats. the list of sound is this:{sound_prompt_list} , default use is "{sound_dir}/discord-notification.mp3".
    and you can designate like this:"{sound_dir}/*.mp3", and ignore .identifier files.
    - Duration: <20 chars → 1–1.5s, 20–50 chars → 2–2.5s, >50 chars → 3–3.5s, system/bot → 1s.
    - Language: If translate=false, keep original; if true, translate all (content, title).

    Output: Valid JSON, double-quoted keys, no explanations, markdown, or extra text.
    **ATTENTION! you cannot print ``` , which is code distinguisher in message like ```json. and you have to change bad words to words that have similar pronounciations or shade particular part.
    for example, fuck -> F--k, 씨발->C발,etc.

    and when the messages contains both message and attachments, you have to sepearate each other sections, and the example is this:
    {'{"name": "퍼리보는사나이","content": "낮선 천장이다", "timestamp": "25. 8. 18. PM 10:18", "attachments": [{ "url": "exmaple_image_url","content_type": "image/jpeg"}]}'}
    -> {'{"name": "퍼리보는사나이","content": "낮선 천장이다","timestamp": "25. 8. 18. PM 10:18",}'}, {'{ "name": "퍼리보는사나이", "timestamp": "25. 8. 18. PM 10:18","content":"", "attachments": [ {"url": "exmaple_image_url", "content_type": "image/jpeg"}]}'},
    YOU MUST PRINT ONLY JSON data and DO NOT CONTAIN ANY DECORATORS LIKE "```json" I SAID TWICE NEVER DO THAT.
    print file into one line.
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
    completion = client.chat.completions.create(
        model=OPENROUTER_MODEL,
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
