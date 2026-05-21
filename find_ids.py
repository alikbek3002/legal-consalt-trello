"""
Вспомогательный скрипт. Запусти ОДИН РАЗ, чтобы узнать ID группы и ID/username
бота-отправителя.

Использование:
    1. Заполни в .env только TG_API_ID, TG_API_HASH, TG_PHONE, TG_SESSION_NAME
       (Trello и TARGET_GROUP_ID можно оставить заглушками — этот скрипт их не читает).
    2. python find_ids.py
    3. В Telegram отправь в нужную группу любое сообщение (или дождись, пока бот-источник
       пришлёт очередную заявку).
    4. Скрипт выведет chat_id и sender_id/username. Скопируй их в .env как
       TARGET_GROUP_ID и SOURCE_BOT_USERNAME.
    5. Останови скрипт по Ctrl+C.
"""
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
PHONE = os.environ["TG_PHONE"]
SESSION = os.environ.get("TG_SESSION_NAME", "session/legalconsalt")

os.makedirs(os.path.dirname(SESSION) or ".", exist_ok=True)

client = TelegramClient(SESSION, API_ID, API_HASH)


@client.on(events.NewMessage())
async def echo(event: events.NewMessage.Event) -> None:
    sender = await event.get_sender()
    chat = await event.get_chat()
    username = getattr(sender, "username", None)
    is_bot = getattr(sender, "bot", False)
    print("─" * 60)
    print(f"chat_id      = {event.chat_id}")
    print(f"chat_title   = {getattr(chat, 'title', '<private>')}")
    print(f"sender_id    = {event.sender_id}")
    print(f"sender_user  = @{username}" if username else "sender_user  = <нет username>")
    print(f"is_bot       = {is_bot}")
    print(f"text (первые 100 симв.): {(event.raw_text or '')[:100]!r}")


async def main() -> None:
    await client.start(phone=PHONE)
    me = await client.get_me()
    print(f"Залогинены как @{me.username or me.first_name} (id={me.id})")
    print("Жду сообщений. Для выхода нажми Ctrl+C.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
