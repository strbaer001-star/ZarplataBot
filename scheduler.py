import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_all_users_with_reminder, get_all_users
from offers import OFFERS

scheduler = AsyncIOScheduler()

async def send_reminders(bot, hour: str):
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
    users = await get_all_users()
    for (user_id,) in users:
        try:
            kb = InlineKeyboardBuilder()
            kb.button(text="▶️ Почати квест", callback_data="choose_category")
            kb.adjust(1)

            await bot.send_message(
                user_id,
                "🔥 Нові офери тижня!\n\n"
                "🥇 O.Bank — 400 грн\n"
                "🥈 ПУМБ — 300 грн\n"
                "🥉 ПриватБанк — 150 грн\n\n"
                "💰 Разом: до 950 грн за ~30 хвилин\n\n"
                "Починаємо? 👇",
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            print(f"Помилка розсилки для {user_id}: {e}")

async def start_scheduler(bot):
    for hour in ["9", "12", "18", "20"]:
        scheduler.add_job(
            send_reminders, "cron", hour=int(hour), minute=0, args=[bot, hour]
        )

    scheduler.add_job(
        send_weekly_digest, "cron", day_of_week="mon", hour=10, minute=0, args=[bot]
    )

    scheduler.start()
    print("✅ Планувальник запущено")
