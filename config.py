import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REQUIRED = [
    "TG_API_ID",
    "TG_API_HASH",
    "TG_PHONE",
    "TG_SESSION_NAME",
    "TARGET_GROUP_ID",
    "SOURCE_BOT_USERNAMES",
    "TRELLO_KEY",
    "TRELLO_TOKEN",
    "TRELLO_LIST_ID",
]

missing = [name for name in REQUIRED if not os.getenv(name)]
if missing:
    print(f"ERROR: в .env не заданы переменные: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

TG_API_ID = int(os.environ["TG_API_ID"])
TG_API_HASH = os.environ["TG_API_HASH"]
TG_PHONE = os.environ["TG_PHONE"]
TG_SESSION_NAME = os.environ["TG_SESSION_NAME"]

TARGET_GROUP_ID = int(os.environ["TARGET_GROUP_ID"])

SOURCE_BOT_USERNAMES = [
    name.strip().lstrip("@")
    for name in os.environ["SOURCE_BOT_USERNAMES"].split(",")
    if name.strip()
]
if not SOURCE_BOT_USERNAMES:
    print("ERROR: SOURCE_BOT_USERNAMES пустой", file=sys.stderr)
    sys.exit(1)

TRELLO_KEY = os.environ["TRELLO_KEY"]
TRELLO_TOKEN = os.environ["TRELLO_TOKEN"]
TRELLO_LIST_ID = os.environ["TRELLO_LIST_ID"]

Path(TG_SESSION_NAME).parent.mkdir(parents=True, exist_ok=True)

# Деплой на Railway/контейнеры: если задана строковая сессия — используем её
# (на хосте нет интерактивного ввода SMS-кода). Локально — файловая сессия.
TG_STRING_SESSION = os.getenv("TG_STRING_SESSION")


def get_session():
    """Сессия для TelegramClient: строковая на проде, файловая локально."""
    if TG_STRING_SESSION:
        from telethon.sessions import StringSession

        return StringSession(TG_STRING_SESSION)
    return TG_SESSION_NAME
