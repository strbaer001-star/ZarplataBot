import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import get_all_users_with_reminder, get_all_users, get_user
from offers import OFFERS

scheduler = AsyncIOScheduler()

async def send_reminders(bot, hour: str):
    """Надсилає нагадування всім хто поставив цей час"""
    users = await get_all_users_with_reminder(f"{hour}:00")
    for user_id, quest_progress in users:
        try:
            progress = json.loads(quest_progress) if quest_progress else {}
            completed = progress.get("completed", [])
            available = progress.get("available", [])
            remaining = [k for k in available if k not in completed]

            if not remaining:
                continue

            next_bank = remaining[0]
            offer = OFFERS.get(next_bank, {})
            remaining_total = sum(OFFERS[k]["bonus"] for k in remaining if k in OFFERS)

            from aiogram.utils.keyboard import InlineKeyboardBuilder
            kb = InlineKeyboardBuilder()
            kb.button(text="▶️ Продовжити!", callback_data=f"step_{next_bank}")
            kb.adjust(1)

            await bot.send_message(
                user_id,
                f"👋 Привіт!\n\n"
                f"Не забув про квест? 😊\n"
                f"Залишилось заробити ще {remaining_total} грн 💰\n\n"
                f"Наступний крок: {offer.get('emoji', '')} {offer.get('name', '')} → {offer.get('bonus_text', '')}\n\n"
                f"Продовжуємо? 👇",
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            print(f"Помилка нагадування для {user_id}: {e}")

async def send_weekly_digest(bot):
    """Щопонеділка надсилає нові офери всім підписникам"""
    users = await get_all_users()
    for (user_id,) in users:
        try:
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            kb = InlineKeyboardBuilder()
            kb.button(text="▶️ Почати квест", callback_data="start_quest")
            kb.adjust(1)

            await bot.send_message(
                user_id,
                "🔥 Нові офери тижня!\n\n"
                "🥇 O.Bank — 400 грн\n"
                "🥈 ПУМБ — 300 грн\n"
                "🥉 ПриватБанк — 150 грн\n"
                "4️⃣ Monobank — 100 грн\n"
                "5️⃣ Sense Bank — 100 грн\n\n"
                "💰 Разом: до 1150 грн за ~50 хвилин\n\n"
                "Починаємо? 👇",
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            print(f"Помилка розсилки для {user_id}: {e}")

async def start_scheduler(bot):
    """Запускає всі заплановані задачі"""

    # Нагадування щогодини в потрібний час
    for hour in ["9", "12", "18", "20"]:
        scheduler.add_job(
            send_reminders,
            "cron",
            hour=int(hour),
            minute=0,
            args=[bot, hour]
        )

    # Щотижнева розсилка — щопонеділка о 10:00
    scheduler.add_job(
        send_weekly_digest,
        "cron",
        day_of_week="mon",
        hour=10,
        minute=0,
        args=[bot]
    )

    scheduler.start()
    print("✅ Планувальник запущено")
