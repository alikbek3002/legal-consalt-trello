"""Пошаговая авторизация Telethon (управляемая, без интерактивного input).

  python tg_auth.py send              — отправить код на телефон
  python tg_auth.py signin <code>     — войти по коду
  python tg_auth.py signin <code> <2fa_password>  — если включена 2FA
"""
import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient, functions
from telethon.errors import SessionPasswordNeededError
from telethon.network import ConnectionTcpObfuscated

load_dotenv()

HASH_FILE = "session/.code_hash.json"


def make_client() -> TelegramClient:
    return TelegramClient(
        os.environ["TG_SESSION_NAME"],
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
        connection=ConnectionTcpObfuscated,
        connection_retries=2,
        retry_delay=2,
    )


async def send() -> None:
    client = make_client()
    await asyncio.wait_for(client.connect(), timeout=30)
    sent = await asyncio.wait_for(
        client.send_code_request(os.environ["TG_PHONE"]), timeout=40
    )
    os.makedirs("session", exist_ok=True)
    with open(HASH_FILE, "w") as f:
        json.dump({"phone_code_hash": sent.phone_code_hash, "type": str(sent.type)}, f)
    print(f"CODE_SENT type={sent.type}", flush=True)
    await client.disconnect()


async def resend() -> None:
    client = make_client()
    await asyncio.wait_for(client.connect(), timeout=30)
    with open(HASH_FILE) as f:
        phone_code_hash = json.load(f)["phone_code_hash"]
    res = await client(
        functions.auth.ResendCodeRequest(
            phone_number=os.environ["TG_PHONE"],
            phone_code_hash=phone_code_hash,
        )
    )
    with open(HASH_FILE, "w") as f:
        json.dump({"phone_code_hash": res.phone_code_hash, "type": str(res.type)}, f)
    print(f"RESENT type={res.type}", flush=True)
    await client.disconnect()


async def signin(code, password=None) -> None:
    client = make_client()
    await asyncio.wait_for(client.connect(), timeout=30)
    with open(HASH_FILE) as f:
        phone_code_hash = json.load(f)["phone_code_hash"]
    try:
        await client.sign_in(
            phone=os.environ["TG_PHONE"],
            code=code,
            phone_code_hash=phone_code_hash,
        )
    except SessionPasswordNeededError:
        if not password:
            print("NEED_2FA_PASSWORD", flush=True)
            await client.disconnect()
            return
        await client.sign_in(password=password)
    me = await client.get_me()
    print(f"SIGNED_IN id={me.id} username=@{me.username} name={me.first_name}", flush=True)
    await client.disconnect()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if cmd == "send":
            asyncio.run(send())
        elif cmd == "resend":
            asyncio.run(resend())
        elif cmd == "signin":
            code = sys.argv[2]
            pw = sys.argv[3] if len(sys.argv) > 3 else None
            asyncio.run(signin(code, pw))
        else:
            print("usage: tg_auth.py send | signin <code> [2fa_password]")
    except asyncio.TimeoutError:
        print("TIMEOUT — соединение зависло (вероятно, флуд-вэйт по IP или блокировка сети)", flush=True)
