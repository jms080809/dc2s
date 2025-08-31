from generate_scenario import genearte_scenario
import datetime as dt
from scrap_discord import extract_chat
from dotenv import load_dotenv
from shorts import generate_discord_chat_shorts
import os
import json

load_dotenv("../.env")
filename = os.getenv("filename")
scenario_src = os.getenv("scenario_src")

load_from_scenario_file = bool(int(os.getenv("load_from_scenario_file")))
if load_from_scenario_file:
    scenario = open(scenario_src).read()
    scenario=json.loads(scenario)
else:
    timezone = dt.timezone(dt.timedelta(hours=9))  # KST

    after = dt.datetime(2025, 8, 29, 12 + 9, 11).astimezone(timezone)
    before = dt.datetime(2025, 8, 29, 12 + 9, 47).astimezone(timezone)

    TOKEN = os.getenv("TOKEN")
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    chat_data = extract_chat(TOKEN, CHANNEL_ID, filename=filename, save=True, after=after, before=before, timezone=timezone)

    scenario = genearte_scenario(content=chat_data.get_data(), save=True, filename=filename)

generate_discord_chat_shorts(scenario=scenario, filename=filename)
#test code never mind
# timezone = dt.timezone(dt.timedelta(hours=9))  # KST

# after = dt.datetime(2025, 8, 29, 12 + 9, 11).astimezone(timezone)
# before = dt.datetime(2025, 8, 29, 12 + 9, 47).astimezone(timezone)

# TOKEN = os.getenv("TOKEN")
# CHANNEL_ID = os.getenv("CHANNEL_ID")

# chat_data = extract_chat(TOKEN, CHANNEL_ID, filename=filename, save=True, after=after, before=before, timezone=timezone)
