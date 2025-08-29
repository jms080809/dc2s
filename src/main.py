from generate_scenario import genearte_scenario
import datetime as dt
from scrap_discord import extract_chat
from dotenv import load_dotenv
from shorts import generate_discord_chat_shorts
import os
import json

# load_dotenv("../.env")

filename = "furry"
af_date = dt.datetime(2025, 8, 29, 9, 11)
bf_date = dt.datetime(2025, 8, 29, 9, 47)

after = dt.datetime.combine(af_date, dt.time.min)
before = dt.datetime.combine(bf_date, dt.time.max)

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

chat_data = extract_chat(TOKEN, CHANNEL_ID, filename=filename, save=True, after=after, before=before)

scenario = genearte_scenario(content=chat_data.get_data(), save=True, filename=filename)
generate_discord_chat_shorts(scenario=scenario, filename=filename)
