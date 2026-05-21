import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.network import ConnectionTcpObfuscated

load_dotenv()


async def main():
    c = TelegramClient(
        os.environ["TG_SESSION_NAME"],
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
        connection=ConnectionTcpObfuscated,
        connection_retries=2,
        retry_delay=2,
    )
    print("connecting...", flush=True)
    await asyncio.wait_for(c.connect(), timeout=30)
    print("authorized:", await c.is_user_authorized(), flush=True)

    gid = int(os.environ["TARGET_GROUP_ID"])
    seen = {}
    n = 0
    async for m in c.iter_messages(gid, limit=40):
        n += 1
        s = await m.get_sender()
        u = getattr(s, "username", None)
        bot = getattr(s, "bot", False)
        key = f"@{u}" if u else f"id={m.sender_id}"
        seen.setdefault(key, (bot, (m.raw_text or "")[:60].replace("\n", " ")))
    print(f"прочитано сообщений: {n}", flush=True)
    for k, (bot, txt) in seen.items():
        print(f"  {k:35} bot={bot}  пример: {txt!r}", flush=True)
    await c.disconnect()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    try:
        asyncio.run(main())
    except asyncio.TimeoutError:
        print("TIMEOUT на connect", flush=True)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", flush=True)
