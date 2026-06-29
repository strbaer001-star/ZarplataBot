# 💰 Зарплата Щодня Bot

Telegram-бот агрегатор реферальних програм українських банків з геймификацією.

## Структура файлів

```
zarplata_bot/
├── main.py          # Запуск бота
├── config.py        # Конфігурація (токен)
├── handlers.py      # Вся логіка розмов
├── database.py      # База даних SQLite
├── offers.py        # Офери банків
├── scheduler.py     # Нагадування і розсилки
├── requirements.txt # Залежності
├── Procfile         # Для Railway
└── .python-version  # Версія Python
```

## Деплой на Railway

### 1. Завантаж код на GitHub
- Створи новий репозиторій `ZarplataBot`
- Завантаж всі файли

### 2. Підключи Railway
- Зайди на railway.app
- New Project → Deploy from GitHub
- Обери репозиторій `ZarplataBot`

### 3. Додай змінну середовища
- В Railway: Variables → New Variable
- Назва: `BOT_TOKEN`
- Значення: твій токен від BotFather

### 4. Бот запущено! ✅

## Що змінити перед запуском

1. В `offers.py` — замінити всі реферальні посилання на свої
2. В `handlers.py` — змінити `@zarplata_shchodnya` на свій канал
3. В `scheduler.py` — змінити текст щотижневої розсилки якщо треба
