"""Разовый тест: берёт последнюю заявку от бота-источника и создаёт карточку Trello."""
import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.network import ConnectionTcpObfuscated

import config
from parser import parse_message
from trello import create_card

load_dotenv()


async def main():
    c = TelegramClient(
        config.TG_SESSION_NAME,
        config.TG_API_ID,
        config.TG_API_HASH,
        connection=ConnectionTcpObfuscated,
        connection_retries=2,
        retry_delay=2,
    )
    await asyncio.wait_for(c.connect(), timeout=30)

    sources = {u.lower() for u in config.SOURCE_BOT_USERNAMES}
    found = None
    async for m in c.iter_messages(config.TARGET_GROUP_ID, limit=80):
        s = await m.get_sender()
        u = (getattr(s, "username", None) or "").lower()
        if u in sources and (m.raw_text or "").strip():
            found = m
            break
    await c.disconnect()

    if not found:
        print("Не нашёл ни одной заявки от ботов в последних 60 сообщениях.", flush=True)
        return

    print(f"Последняя заявка (msg_id={found.id}):", flush=True)
    print("-" * 60, flush=True)
    print(found.raw_text, flush=True)
    print("-" * 60, flush=True)

    parsed = parse_message(found.raw_text)
    parsed["description"] += f"\n\n---\n[ТЕСТ] tg_msg_id={found.id}"
    card = await create_card(**parsed)
    print(f"Карточка создана: {card.get('shortUrl')}", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    asyncio.run(main())
