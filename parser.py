import re

TITLE_MAX = 100

# Заявки Fusion AI Agent приходят в двух форматах:
#   Формат A («Оператор, нужна помощь!»):  👤 Клиент: X / 📡 Канал: Y / 💬 Причина: Z
#   Формат B («Агент собрал данные!»):      📡 Канал: Y / - Имя клиента: X / - Номер телефона: P
CLIENT_RE = re.compile(r"👤\s*Клиент:\s*(.+)")
NAME_RE = re.compile(r"-\s*Имя клиента:\s*(.+)")
PHONE_RE = re.compile(r"-\s*Номер телефона:\s*(.+)")
CHANNEL_RE = re.compile(r"📡\s*Канал:\s*(.+)")
REASON_RE = re.compile(r"💬\s*Причина:\s*(.+)")

# Маркеры сообщений, которые НЕ являются заявками клиента
# (системные уведомления — для них карточки не создаём).
NON_LEAD_MARKERS = (
    "Подписка скоро истекает",
    "Дата истечения",
    "Продлить подписку",
)


def is_lead(text: str) -> bool:
    """False для системных сообщений (напоминания о подписке и т.п.)."""
    t = text or ""
    return not any(marker in t for marker in NON_LEAD_MARKERS)


def parse_message(text: str) -> dict[str, str]:
    """
    Превращает текст заявки в поля Trello-карточки.

    Заголовок: «<имя> (<канал>) — <причина/телефон>».
    Описание: весь текст заявки как есть.
    Если маркеров нет (другой формат) — заголовок = первая непустая строка.
    """
    text = (text or "").strip()
    if not text:
        return {"title": "(пустая заявка)", "description": ""}

    client = _search(CLIENT_RE, text) or _search(NAME_RE, text)
    channel = _search(CHANNEL_RE, text)
    reason = _search(REASON_RE, text)
    phone = _search(PHONE_RE, text)

    if client or channel:
        parts = []
        if client:
            parts.append(client)
        if channel:
            parts.append(f"({channel})")
        title = " ".join(parts)
        tail = reason or phone
        if tail:
            title += f" — {tail}"
    else:
        title = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Новая заявка")

    return {"title": title[:TITLE_MAX], "description": text}


def _search(pattern: "re.Pattern", text: str):
    m = pattern.search(text)
    return m.group(1).strip() if m else None
