"""Одноразовая утилита: выводит все группы/каналы с их chat_id."""
import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


async def main() -> None:
    client = TelegramClient(
        os.environ["TG_SESSION_NAME"],
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
    )
    await client.connect()
    if not await client.is_user_authorized():
        print("NOT_AUTHORIZED — сессия не валидна, нужна повторная авторизация", flush=True)
        await client.disconnect()
        return

    print(f"{'ID':>16}  {'Тип':<10}  Название", flush=True)
    print("-" * 70, flush=True)
    count = 0
    async for d in client.iter_dialogs(limit=300):
        if d.is_group or d.is_channel:
            kind = "channel" if d.is_channel and not d.is_group else "group"
            print(f"{d.id:>16}  {kind:<10}  {d.name}", flush=True)
            count += 1
    print(f"\nИтого: {count} групп/каналов", flush=True)
    await client.disconnect()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    asyncio.run(main())
