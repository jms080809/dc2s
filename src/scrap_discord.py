import requests
import datetime as dt
import json
import os.path
from time import sleep


# wrapper class for recognition
class ChatRawData:
    def __init__(self, rawdata):
        try:
            self.chatters: dict = rawdata["chatters"]
            self.contents: dict = rawdata["contents"]
        except Exception as err:
            print(err)
            self.chatters: dict = {}
            self.contents: dict = {}

    def get_data(self):
        return {"chatters": self.chatters, "contents": self.contents}


def datetime_to_snowflake(dt: dt.datetime) -> int:
    discord_epoch = 1420070400000
    timestamp_ms = int(dt.timestamp() * 1000)
    return (timestamp_ms - discord_epoch) << 22


def extract_chat(
    token: str,
    channel_id: str,
    filename: str,
    # if you remain blank, it will get recent chats of today
    before: dt.date = dt.datetime.combine(dt.datetime.now().date(), dt.time(hour=23, minute=59, second=59)),
    after: dt.date = dt.datetime.combine(dt.datetime.now() - dt.timedelta(days=1), dt.time(hour=23, minute=59, second=59)),
    save: bool = False,
) -> ChatRawData:
    # CAUTION!! copy your user token when you want your dm, and use bot token when not
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.139 Safari/537.36",
    }
    # setting for extraction
    chatters_r = set()
    chatters = {}
    contents = []

    before = dt.datetime.combine(before, dt.time(hour=23, minute=59, second=59))
    after = dt.datetime.combine(after, dt.time(hour=23, minute=59, second=59))
    for i in range((before.date() - after.date()).days):
        b, a = dt.datetime.now() - dt.timedelta(i), dt.datetime.now() - dt.timedelta(i + 1)
        # crawl part of each
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?before={datetime_to_snowflake(b)}&after={datetime_to_snowflake(a)}&limit=100"
        res = requests.request(method="GET", url=url, headers=headers)
        if res.status_code != 200:
            return None
        chat_data = res.json()

        # extracting for each data between dates
        for msg in chat_data:
            name: str = msg["author"]["username"] if msg["author"]["global_name"] == None else msg["author"]["global_name"]
            avatar: str = ""
            avatar = f'https://cdn.discordapp.com/avatars/{msg["author"]["id"]}/{msg["author"]["avatar"]}.png?size=128'
            content = msg["content"]
            timestamp = dt.datetime.fromisoformat(msg["timestamp"])

            chatter_sector = (name, avatar)
            content_sector = {
                "name": name,
                "content": content,
                "timestamp": timestamp,
            }
            chatters_r.add(chatter_sector)
            contents.append(content_sector)
        sleep(0.1)

    # enrolling functions
    for chatter in chatters_r:
        chatters[chatter[0]] = {"name": chatter[0], "avatar": chatter[1]}
    extracted_data = {"chatters": chatters, "contents": contents}
    if save:
        file_src = f"./chats/{filename}.json"
        if os.path.isfile(file_src):
            os.remove(file_src)
        with open(file_src, "+a") as f:
            f.write(json.dumps(extracted_data, ensure_ascii=False))
    print("done!")
    return extracted_data


# test
TOKEN = "쏼라쏼라니가입력하세요ㅇㅇ"
CHANNEL_ID = "응숫자니가넣어"

a = extract_chat(TOKEN, CHANNEL_ID, "furry", save=True, after=dt.date(2025, 1, 1))
# print(a.get_data())

with open("./chats/furry.json") as f:
    b = ChatRawData(rawdata=json.load(f))
    print(len(b.contents))

# ill scrap for a test right side thanks

# it will make me money haha i think? idk i made just for fun
# ill open this to everyone in github, program sharing place
