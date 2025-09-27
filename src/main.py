import os
import json
import uuid
import datetime as dt
from dotenv import load_dotenv
from simpleeval import simple_eval

from generate_scenario import generate_scenario
from scrap_discord import extract_chat
from shorts import generate_discord_chat_shorts


def load_config(env_path: str = "../.env") -> dict:
    """Load environment variables from .env and return as dict."""
    load_dotenv(env_path)

    return {
        "filename": os.getenv("filename") or "아쎄이! 기열! 오도짜세 해변님 나가신다",
        "scenario_src": os.getenv("scenario_src"),
        "load_from_file": bool(int(os.getenv("load_from_scenario_file", "0"))),
        "after": os.getenv("after"),
        "before": os.getenv("before"),
        "token": os.getenv("TOKEN"),
        "channel_id": os.getenv("CHANNEL_ID"),
    }


def parse_datetime(expr: str, timezone: dt.timezone) -> dt.datetime:
    """Convert underscore-separated datetime string into datetime object."""
    return dt.datetime(*map(simple_eval, expr.split("_"))).astimezone(timezone)


def load_scenario_from_file(path: str) -> dict:
    """Load scenario JSON from file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_scenario(config: dict) -> dict:
    """Build scenario either from file or by extracting Discord chat."""
    if config["load_from_file"]:
        return load_scenario_from_file(config["scenario_src"])

    timezone = dt.timezone(dt.timedelta(hours=9))  # KST
    after = parse_datetime(config["after"], timezone)
    before = parse_datetime(config["before"], timezone)

    chat_data = extract_chat(
        config["token"],
        config["channel_id"],
        filename=config["filename"],
        save=True,
        after=after,
        before=before,
        timezone=timezone,
    )
    return generate_scenario(
        content=chat_data.get_data(), save=True, filename=config["filename"]
    )


def main():
    config = load_config()
    scenario = build_scenario(config)

    output_filename = f"{config['filename']}_{uuid.uuid1()}"
    generate_discord_chat_shorts(
        scenario=scenario,
        filename=output_filename,
        message_font="./asset/fonts/SejongGeulggot.ttf",
    )


if __name__ == "__main__":
    main()
