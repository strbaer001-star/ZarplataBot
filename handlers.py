import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_user, create_user, update_user
from offers import OFFERS, BANK_NAMES, get_available_offers, calculate_total

router = Router()

class QuestState(StatesGroup):
    selecting_banks = State()
    in_quest = State()
    waiting_reminder = State()

def progress_bar(current: int, total: int) -> str:
    if total == 0:
        return "🟩🟩🟩🟩🟩"
    filled = int((current / total) * 5)
    return "🟩" * filled + "⬜" * (5 - filled)

# ───────────────────────────────────────────
# СТАРТ
# ───────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await create_user(message.from_user.id, message.from_user.username or "")
    user = await get_user(message.from_user.id)

    # Якщо вже є прогрес — показати меню
    if user and user[3]:  # quest_progress
        await show_main_menu(message)
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Почати!", callback_data="start_quest")
    kb.button(text="ℹ️ Як це працює?", callback_data="how_it_works")
    kb.adjust(1)

    await message.answer(
        "👋 Привіт!\n\n"
        "Я допомагаю українцям заробляти на бонусах від банків.\n\n"
        "Ніяких інвестицій. Ніяких ризиків.\n"
        "Просто реєструєшся — отримуєш гроші на картку 💰\n\n"
        "Поїхали? 👇",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "how_it_works")
async def how_it_works(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Поїхали!", callback_data="start_quest")

    await callback.message.edit_text(
        "Все просто:\n\n"
        "1️⃣ Ти реєструєшся в банку за моїм посиланням\n"
        "2️⃣ Банк платить тобі бонус (100–400 грн)\n"
        "3️⃣ Гроші приходять на картку 💳\n\n"
        "Банки платять за нових клієнтів — це офіційні програми.\n"
        "Жодного підступу ✅",
        reply_markup=kb.as_markup()
    )

# ───────────────────────────────────────────
# ВИБІР БАНКІВ
# ───────────────────────────────────────────
@router.callback_query(F.data == "start_quest")
async def select_banks(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestState.selecting_banks)
    await state.update_data(selected=[])
    await show_bank_selection(callback.message, [], edit=True)

async def show_bank_selection(message: Message, selected: list, edit: bool = False):
    kb = InlineKeyboardBuilder()
    for key, name in BANK_NAMES.items():
        check = "☑️" if key in selected else "⬜"
        kb.button(text=f"{check} {name}", callback_data=f"toggle_{key}")
    kb.button(text="✅ Готово!", callback_data="banks_done")
    kb.adjust(2, 2, 2, 1)

    text = (
        "Відміть банки де ти вже клієнт 👇\n"
        "(пропустимо їх і покажемо тільки нові можливості)\n\n"
        "Немає жодного — просто натисни ✅ Готово!"
    )

    if edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_bank(callback: CallbackQuery, state: FSMContext):
    bank = callback.data.replace("toggle_", "")
    data = await state.get_data()
    selected = data.get("selected", [])

    if bank in selected:
        selected.remove(bank)
    else:
        selected.append(bank)

    await state.update_data(selected=selected)
    await show_bank_selection(callback.message, selected, edit=True)

@router.callback_query(F.data == "banks_done")
async def banks_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected", [])

    await update_user(callback.from_user.id, "registered_banks", json.dumps(selected))

    available = get_available_offers(selected)

    if not available:
        await callback.message.edit_text(
            "😮 Ти вже зареєстрований у всіх банках!\n\n"
            "🔔 Я сповіщу тебе коли з'являться нові офери.\n\n"
            "Слідкуй за каналом: @zarplata_shchodnya"
        )
        return

    total = calculate_total(available)
    progress = json.dumps({"current": 0, "completed": [], "available": [k for k, _ in available]})
    await update_user(callback.from_user.id, "quest_progress", progress)
    await state.set_state(QuestState.in_quest)

    quest_text = "🎯 Твій персональний маршрут:\n\n"
    for i, (key, offer) in enumerate(available, 1):
        quest_text += f"⬜ Крок {i}: {offer['emoji']} {offer['name']} → {offer['bonus_text']} ({offer['time']})\n"

    quest_text += f"\n💰 Разом: {total} грн за ~{len(available) * 10} хвилин\n"
    quest_text += f"\n{progress_bar(0, total)} 0 / {total} грн"

    kb = InlineKeyboardBuilder()
    kb.button(text="▶️ Почати крок 1", callback_data=f"step_{available[0][0]}")
    kb.button(text="🕐 Почати пізніше", callback_data="remind_later")
    kb.adjust(1)

    await callback.message.edit_text(quest_text, reply_markup=kb.as_markup())

# ───────────────────────────────────────────
# ВИКОНАННЯ КРОКУ
# ───────────────────────────────────────────
@router.callback_query(F.data.startswith("step_"))
async def show_step(callback: CallbackQuery, state: FSMContext):
    bank_key = callback.data.replace("step_", "")
    offer = OFFERS.get(bank_key)
    if not offer:
        return

    conditions = "\n".join([f"   {i+1}. {c}" for i, c in enumerate(offer["conditions"])])

    kb = InlineKeyboardBuilder()
    kb.button(text="👉 Перейти за посиланням", url=offer["link"])
    kb.button(text="✅ Виконав!", callback_data=f"done_{bank_key}")
    kb.button(text="❓ Не виходить", callback_data=f"help_{bank_key}")
    kb.button(text="⏸ Зупинити на сьогодні", callback_data="pause_quest")
    kb.adjust(1)

    await callback.message.edit_text(
        f"💳 {offer['emoji']} {offer['name']} — {offer['bonus_text']}\n\n"
        f"⏱ Час: {offer['time']}\n"
        f"⭐ Оцінка: {offer['rating']}\n\n"
        f"✅ Що потрібно зробити:\n{conditions}\n\n"
        f"⚠️ {offer['note']}\n\n"
        f"💰 Отримуєш: {offer['bonus_text']} на картку",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("done_"))
async def step_done(callback: CallbackQuery, state: FSMContext):
    bank_key = callback.data.replace("done_", "")
    offer = OFFERS.get(bank_key)
    user = await get_user(callback.from_user.id)

    progress = json.loads(user[3]) if user[3] else {}
    completed = progress.get("completed", [])
    available = progress.get("available", [])

    if bank_key not in completed:
        completed.append(bank_key)

    current_earned = sum(OFFERS[k]["bonus"] for k in completed if k in OFFERS)
    total = sum(OFFERS[k]["bonus"] for k in available if k in OFFERS)

    progress["completed"] = completed
    progress["current"] = current_earned
    await update_user(callback.from_user.id, "quest_progress", json.dumps(progress))
    await update_user(callback.from_user.id, "total_earned", current_earned)

    remaining = [k for k in available if k not in completed]

    bar = progress_bar(current_earned, total)

    if not remaining:
        await callback.message.edit_text(
            f"🏆 Квест завершено!\n\n"
            f"Ти пройшов всі кроки і заробив до {total} грн 🎉\n\n"
            f"{bar} {current_earned} / {total} грн\n\n"
            f"Бонуси надходять протягом 1–3 днів після виконання умов кожного банку.\n\n"
            f"🔔 Щопонеділка надсилаю нові офери!\n"
            f"Підпишись на канал: @zarplata_shchodnya"
        )
        return

    next_bank = remaining[0]
    next_offer = OFFERS[next_bank]

    kb = InlineKeyboardBuilder()
    kb.button(text=f"▶️ Крок {len(completed)+1}: {next_offer['name']}", callback_data=f"step_{next_bank}")
    kb.button(text="🕐 Продовжити завтра", callback_data="pause_quest")
    kb.adjust(1)

    await callback.message.edit_text(
        f"🎉 Виконано! +{offer['bonus_text']}\n\n"
        f"{bar} {current_earned} / {total} грн\n\n"
        f"Залишилось ще {len(remaining)} кроки на {sum(OFFERS[k]['bonus'] for k in remaining if k in OFFERS)} грн\n\n"
        f"Продовжуємо? 💪",
        reply_markup=kb.as_markup()
    )

# ───────────────────────────────────────────
# ДОПОМОГА
# ───────────────────────────────────────────
@router.callback_query(F.data.startswith("help_"))
async def help_step(callback: CallbackQuery):
    bank_key = callback.data.replace("help_", "")

    kb = InlineKeyboardBuilder()
    kb.button(text="📲 Не можу встановити додаток", callback_data=f"help_install_{bank_key}")
    kb.button(text="🪪 Проблема з верифікацією", callback_data=f"help_verify_{bank_key}")
    kb.button(text="💳 Не можу оформити картку", callback_data=f"help_card_{bank_key}")
    kb.button(text="◀️ Назад", callback_data=f"step_{bank_key}")
    kb.adjust(1)

    await callback.message.edit_text(
        "Що саме не виходить? 👇\n"
        "Обери проблему і я поясню покроково:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("help_install_"))
async def help_install(callback: CallbackQuery):
    bank_key = callback.data.replace("help_install_", "")
    offer = OFFERS.get(bank_key)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Встановив, йду далі", callback_data=f"step_{bank_key}")
    kb.button(text="😕 Все одно не виходить", callback_data=f"help_{bank_key}")

    await callback.message.edit_text(
        f"📲 Як встановити {offer['name']}:\n\n"
        f"1. Відкрий App Store (iPhone) або Google Play (Android)\n"
        f"2. Введи в пошуку '{offer['name']}'\n"
        f"3. Натисни 'Встановити'\n"
        f"4. Після встановлення — відкрий і натисни 'Реєстрація'\n\n"
        f"💡 Якщо не знайшов — спробуй пошукати повну назву банку",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("help_verify_"))
async def help_verify(callback: CallbackQuery):
    bank_key = callback.data.replace("help_verify_", "")

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Верифікувався", callback_data=f"step_{bank_key}")
    kb.button(text="😕 Ще є питання", callback_data=f"help_{bank_key}")

    await callback.message.edit_text(
        "🪪 Верифікація через Дію — найшвидший спосіб:\n\n"
        "1. Переконайся що Дія встановлена і документи завантажені\n"
        "2. В банківському додатку обери 'Верифікація через Дію'\n"
        "3. Дозволи доступ і підтверди\n"
        "4. Готово — займає 2–3 хвилини ✅\n\n"
        "Немає Дії? Альтернативи:\n"
        "— Фото паспорта + селфі\n"
        "— Відео-дзвінок з оператором (10–15 хв)",
        reply_markup=kb.as_markup()
    )

# ───────────────────────────────────────────
# ПАУЗА І НАГАДУВАННЯ
# ───────────────────────────────────────────
@router.callback_query(F.data == "pause_quest")
async def pause_quest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestState.waiting_reminder)

    kb = InlineKeyboardBuilder()
    for time in ["9:00", "12:00", "18:00", "20:00"]:
        kb.button(text=time, callback_data=f"remind_{time}")
    kb.button(text="🚫 Не нагадувати", callback_data="no_remind")
    kb.adjust(2, 2, 1)

    await callback.message.edit_text(
        "Добре, зупиняємось 👌\n\n"
        "Твій прогрес збережено.\n\n"
        "О котрій нагадати завтра? 🕐",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("remind_"))
async def set_reminder(callback: CallbackQuery, state: FSMContext):
    time = callback.data.replace("remind_", "")
    await update_user(callback.from_user.id, "reminder_time", time)
    await state.clear()

    await callback.message.edit_text(
        f"✅ Нагадаю завтра о {time}!\n\n"
        f"А поки підпишись на канал щоб не пропустити нові офери:\n"
        f"👉 @zarplata_shchodnya"
    )

@router.callback_query(F.data == "no_remind")
async def no_reminder(callback: CallbackQuery, state: FSMContext):
    await update_user(callback.from_user.id, "reminder_time", None)
    await state.clear()

    await callback.message.edit_text(
        "Добре! Повернись коли будеш готовий — твій прогрес збережено 💾\n\n"
        "Просто напиши /start щоб продовжити."
    )

@router.callback_query(F.data == "remind_later")
async def remind_later(callback: CallbackQuery, state: FSMContext):
    await pause_quest(callback, state)

# ───────────────────────────────────────────
# ГОЛОВНЕ МЕНЮ (для тих хто вже проходив)
# ───────────────────────────────────────────
async def show_main_menu(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎯 Нові офери тижня", callback_data="weekly_offers")
    kb.button(text="📊 Мій прогрес", callback_data="my_progress")
    kb.button(text="🔄 Почати новий квест", callback_data="start_quest")
    kb.adjust(1)

    await message.answer(
        "👋 З поверненням!\n\n"
        "Що бажаєш?",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    total_earned = user[6] if user else 0

    progress = json.loads(user[3]) if user and user[3] else {}
    completed = progress.get("completed", [])
    available = progress.get("available", [])

    completed_text = ""
    for key in completed:
        if key in OFFERS:
            completed_text += f"✅ {OFFERS[key]['name']} — {OFFERS[key]['bonus_text']}\n"

    total = sum(OFFERS[k]["bonus"] for k in available if k in OFFERS)
    current = sum(OFFERS[k]["bonus"] for k in completed if k in OFFERS)

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Назад", callback_data="back_to_menu")

    await callback.message.edit_text(
        f"📊 Твій прогрес:\n\n"
        f"{progress_bar(current, total)} {current} / {total} грн\n\n"
        f"{completed_text if completed_text else 'Ще не виконано жодного кроку'}\n"
        f"💰 Всього зароблено: {total_earned} грн",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "weekly_offers")
async def weekly_offers(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="▶️ Почати квест", callback_data="start_quest")
    kb.button(text="◀️ Назад", callback_data="back_to_menu")
    kb.adjust(1)

    await callback.message.edit_text(
        "🔥 ТОП бонусів цього тижня:\n\n"
        "🥇 O.Bank — 400 грн (найвигідніше)\n"
        "🥈 ПУМБ — 300 грн\n"
        "🥉 ПриватБанк — 150 грн\n"
        "4️⃣ Monobank — 100 грн\n"
        "5️⃣ Sense Bank — 100 грн\n\n"
        "💰 Разом квест: до 1150 грн\n\n"
        "Підпишись на канал щоб не пропустити нові офери:\n"
        "👉 @zarplata_shchodnya",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎯 Нові офери тижня", callback_data="weekly_offers")
    kb.button(text="📊 Мій прогрес", callback_data="my_progress")
    kb.button(text="🔄 Почати новий квест", callback_data="start_quest")
    kb.adjust(1)

    await callback.message.edit_text(
        "👋 Головне меню\n\n"
        "Що бажаєш?",
        reply_markup=kb.as_markup()
    )
