import asyncio

import httpx
from loguru import logger

import config

API_URL = "https://api.trello.com/1/cards"


async def create_card(title: str, description: str = "") -> dict:
    params = {
        "key": config.TRELLO_KEY,
        "token": config.TRELLO_TOKEN,
        "idList": config.TRELLO_LIST_ID,
        "name": title[:16384],
        "desc": description[:16384],
        "pos": "top",
    }

    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=20.0) as client:
        for attempt in (1, 2, 3):
            try:
                r = await client.post(API_URL, params=params)
                if r.status_code == 200:
                    card = r.json()
                    logger.info(f"Trello card created: {card.get('shortUrl')}")
                    return card
                if r.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"Trello {r.status_code}, попытка {attempt}/3: {r.text[:200]}"
                    )
                    await asyncio.sleep(2 * attempt)
                    continue
                r.raise_for_status()
            except httpx.HTTPError as exc:
                last_exc = exc
                logger.warning(f"HTTP error попытка {attempt}/3: {exc}")
                await asyncio.sleep(2 * attempt)

    raise RuntimeError(f"Не удалось создать карточку Trello после 3 попыток: {last_exc}")


if __name__ == "__main__":
    import sys

    title = sys.argv[1] if len(sys.argv) > 1 else "Test card from script"
    desc = sys.argv[2] if len(sys.argv) > 2 else "Если ты это видишь — Trello API работает."
    result = asyncio.run(create_card(title, desc))
    print(result.get("shortUrl"))
