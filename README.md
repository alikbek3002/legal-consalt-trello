# LegalConsalt: Telegram → Trello

Скрипт на Python, который слушает Telegram-группу и автоматически создаёт карточки в Trello, когда бот-источник присылает туда новую заявку.

Использует **Telethon** (пользовательский аккаунт через MTProto), потому что классические Telegram-боты не имеют права читать сообщения других ботов в группах — это политика Telegram.

---

## Что в проекте

| Файл | Назначение |
|---|---|
| `userbot.py` | Основная точка входа. Слушает группу, ловит заявки, создаёт карточки. |
| `find_ids.py` | Одноразовый помощник: показывает `chat_id` и `sender_id`. |
| `parser.py` | Превращает текст заявки в `{title, description}`. |
| `trello.py` | Создаёт карточки через REST API Trello. |
| `config.py` | Загружает `.env`. |
| `.env.example` | Шаблон переменных окружения. |
| `legalconsalt.service` | systemd unit для VPS. |

---

## Шаг 1. Подготовка локально (Mac)

```bash
cd "/Users/alikbekmukanbetov/Desktop/LegalConsalt Trello"

# Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Создать .env по шаблону
cp .env.example .env
```

## Шаг 2. Получить Telegram API credentials

1. Зайти на https://my.telegram.org своим номером.
2. → **API development tools** → создать приложение (любое имя, например `legalconsalt`).
3. Скопировать **`api_id`** и **`api_hash`** в `.env`:
   ```
   TG_API_ID=1234567
   TG_API_HASH=...
   TG_PHONE=+7...
   ```

> **Безопасность:** рекомендую завести **отдельный аккаунт Telegram** (виртуальный номер) для этой задачи. Файл `.session` равноценен паролю — кто его скопировал, тот залогинен под этим аккаунтом.

## Шаг 3. Узнать ID группы и бота-источника

В `.env` пока можно оставить заглушки для `TARGET_GROUP_ID`, `SOURCE_BOT_USERNAME` и блока Trello — `find_ids.py` их не использует.

```bash
python find_ids.py
```

При первом запуске Telethon спросит:
- код из Telegram (придёт в самом мессенджере);
- пароль 2FA (если включён).

После этого появятся строки вида:
```
chat_id      = -1001234567890
sender_user  = @zayavki_bot
is_bot       = True
```

Дожидаемся, пока бот-источник пришлёт хоть одно сообщение в группу. Копируем `chat_id` в `TARGET_GROUP_ID`, а username (без `@`) — в `SOURCE_BOT_USERNAME`. Останавливаем скрипт `Ctrl+C`.

## Шаг 4. Получить ключи Trello

1. https://trello.com/power-ups/admin → создать Power-Up (любое имя).
2. Вкладка **API key** → скопировать `key` → в `.env` `TRELLO_KEY`.
3. На той же странице — **Token** → авторизовать → скопировать в `TRELLO_TOKEN`.
4. ID списка (колонки): открыть нужную доску, добавить `.json` в конце URL (`https://trello.com/b/abc123/board.json`), найти нужный список и его `id` → в `.env` `TRELLO_LIST_ID`.

## Шаг 5. Тест Trello отдельно

```bash
python trello.py "Тест" "Если ты это видишь — Trello работает"
```

В нужной колонке должна появиться карточка. Если нет — проверь `TRELLO_KEY/TOKEN/LIST_ID`.

## Шаг 6. Запуск локально

```bash
python userbot.py
```

В логах:
```
Залогинены как ... (id=...)
Слушаю группу -100..., источник @zayavki_bot
```

Дождись следующей заявки от бота-источника — в Trello должна появиться карточка с пометкой `tg_msg_id=...` в описании.

---

## Шаг 7. Деплой на VPS

Когда локально всё работает:

```bash
# на VPS (Ubuntu/Debian)
sudo adduser --system --group legalconsalt
sudo mkdir -p /opt/legalconsalt
sudo chown legalconsalt:legalconsalt /opt/legalconsalt
```

С локальной машины:
```bash
# Заливаем код И уже созданный .session (чтобы не вводить SMS на VPS)
rsync -av --exclude='.venv' --exclude='__pycache__' \
  ./ user@vps:/opt/legalconsalt/
```

На VPS:
```bash
cd /opt/legalconsalt
sudo -u legalconsalt python3 -m venv .venv
sudo -u legalconsalt .venv/bin/pip install -r requirements.txt

# Защита секретов
sudo chmod 600 .env session/*.session
sudo chown -R legalconsalt:legalconsalt .

# systemd
sudo cp legalconsalt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now legalconsalt

# Логи
sudo journalctl -u legalconsalt -f
```

После `reboot` сервис поднимется сам.

---

## Что нужно доработать

1. **`parser.py`** — сейчас режим-заглушка (первая строка → заголовок, весь текст → описание). Пришли пример сообщения от бота-источника, и сделаем извлечение полей (имя, телефон, услуга).
2. **Защита от дублей** — пока её нет. Если очень надо, добавим поиск карточки по `tg_msg_id` перед созданием.

---

## Структура сообщения от бота-источника

Когда пришлёшь пример — добавим его сюда и опишем разбор.
