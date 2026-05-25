import asyncio
import logging

from loguru import logger
from telethon import TelegramClient, events
from telethon.network import ConnectionTcpObfuscated
from telethon.tl.types import MessageEntityTextUrl

import config
from parser import is_lead, parse_message
from trello import create_card

logging.basicConfig(
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logging.getLogger("telethon").setLevel(logging.INFO)

client = TelegramClient(
    config.get_session(),
    config.TG_API_ID,
    config.TG_API_HASH,
    connection=ConnectionTcpObfuscated,
    connection_retries=5,
    retry_delay=3,
)


@client.on(
    events.NewMessage(
        chats=config.TARGET_GROUP_ID,
        from_users=config.SOURCE_BOT_USERNAMES,
    )
)
async def on_application(event: events.NewMessage.Event) -> None:
    text = event.raw_text or ""
    msg_id = event.message.id

    if not is_lead(text):
        logger.info(f"Пропущено (не заявка, напр. напоминание о подписке) msg_id={msg_id}")
        return

    logger.info(f"Получена заявка msg_id={msg_id}, длина {len(text)} символов")

    parsed = parse_message(text)

    # Достаём спрятанные за гиперссылками URL (напр. «Перейти в диалог»).
    links = [
        e.url
        for e in (event.message.entities or [])
        if isinstance(e, MessageEntityTextUrl)
    ]

    footer = f"---\ntg_msg_id={msg_id}"
    if links:
        footer += "\n🔗 Диалог: " + "\n🔗 ".join(links)
    parsed["description"] = f"{parsed['description']}\n\n{footer}"

    try:
        await create_card(**parsed)
    except Exception as exc:
        logger.exception(f"Не удалось создать карточку для msg_id={msg_id}: {exc}")


async def main() -> None:
    print("Подключаюсь к Telegram… (10-20 секунд)", flush=True)
    await client.connect()
    if not await client.is_user_authorized():
        logger.error(
            "Сессия не авторизована. На проде задай TG_STRING_SESSION, "
            "локально — запусти tg_auth.py для входа по коду."
        )
        return
    me = await client.get_me()
    logger.info(f"Залогинены как {me.username or me.first_name} (id={me.id})")
    logger.info(
        f"Слушаю группу {config.TARGET_GROUP_ID}, "
        f"источники: {', '.join('@' + u for u in config.SOURCE_BOT_USERNAMES)}"
    )
    logger.info("Жду заявок. Ctrl+C для остановки.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
