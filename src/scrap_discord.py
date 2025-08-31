import requests
import datetime as dt
import json
import os.path
import utils


# wrapper class for recognition
class ChatRawData:
    def __init__(self, rawdata):
        try:
            self.chatters: dict = rawdata["chatters"]
            self.contents: dict = rawdata["contents"]
        except Exception as err:
            print(f"Error initializing ChatRawData: {err}")
            self.chatters: dict = {}
            self.contents: dict = {}

    def get_data(self):
        return {"chatters": self.chatters, "contents": self.contents}


def datetime_to_snowflake(dt: dt.datetime) -> int:
    discord_epoch = 1420070400000
    timestamp_ms = int(dt.timestamp() * 1000)
    return (timestamp_ms - discord_epoch) << 22


@utils.debug_print
def extract_chat(
    token: str,
    channel_id: str,
    filename: str,
    timezone: dt.timezone,
    before: dt.datetime = dt.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999),
    after: dt.datetime = (dt.datetime.now() - dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
    save: bool = False,
) -> ChatRawData:
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.139 Safari/537.36",
    }

    chatters_r = set()
    chatters = {}
    contents = []

    after_snowflake = datetime_to_snowflake(after)
    before_utc = before.astimezone(dt.timezone.utc)  # UTC로 변환된 before


    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?after={after_snowflake}&limit=100"
    while url:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Error {res.status_code} while fetching messages between {after} and {before}")
            return ChatRawData({"chatters": {}, "contents": []})

        chat_data = res.json()

        for msg in chat_data:
            msg_timestamp = dt.datetime.fromisoformat(msg["timestamp"]).astimezone(dt.timezone.utc)
            if msg_timestamp < after.astimezone(dt.timezone.utc) or msg_timestamp > before_utc:
                continue  # 시간 범위 밖 메시지 제외
            name = msg["author"]["username"] if msg["author"]["global_name"] is None else msg["author"]["global_name"]
            avatar = f'https://cdn.discordapp.com/avatars/{msg["author"]["id"]}/{msg["author"]["avatar"]}.png?size=128'
            content = msg["content"]
            timestamp = utils.format_datetime(dt.datetime.fromisoformat(msg["timestamp"]).astimezone(timezone))
            attachments = list(map(utils.attachment_align, msg["attachments"]))
            print(attachments)
            chatter_sector = (name, avatar)
            content_sector = {"name": name, "content": content, "timestamp": timestamp, "attachments": attachments}
            chatters_r.add(chatter_sector)
            contents.append(content_sector)

        if len(chat_data) < 100:
            break  # 더 이상 메시지 없음
        last_msg_id = chat_data[-1]["id"]
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?after={last_msg_id}&limit=100"

    for chatter in chatters_r:
        chatters[chatter[0]] = {"name": chatter[0], "avatar": chatter[1]}
    contents.reverse()
    extracted_data = {"chatters": chatters, "contents": contents}

    if save:
        file_src = f"./chats/{filename}.json"
        if os.path.isfile(file_src):
            os.remove(file_src)
        with open(file_src, "w", encoding="utf-8") as f:
            f.write(json.dumps(extracted_data, indent=2))

    return ChatRawData(extracted_data)