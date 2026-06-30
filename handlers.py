import json
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_user, create_user, update_user
from offers import OFFERS
from ai_support import ask_ai, notify_admin

router = Router()

class QuestState(StatesGroup):
    selecting_category = State()
    selecting_level = State()
    selecting_banks = State()
    in_quest = State()
    waiting_reminder = State()
    asking_support = State()

def progress_bar(current: int, total: int) -> str:
    if total == 0:
        return "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%"
    pct = int((current / total) * 100)
    filled = int((current / total) * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)
    return f"{bar} {pct}%"

def divider() -> str:
    return "━━━━━━━━━━━━━━━━━━━━━"

def with_support_button(kb: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
    """Додає кнопку підтримки до будь-якої клавіатури"""
    kb.button(text="🆘 Підтримка", callback_data="open_support")
    return kb

# ═══════════════════════════════════════════
# СТАРТ
# ═══════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await create_user(message.from_user.id, message.from_user.username or "")
    name = message.from_user.first_name or "друже"

    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Почати заробляти", callback_data="choose_category")
    kb.button(text="📊 Мій прогрес", callback_data="my_progress")
    kb.button(text="ℹ️ Як це працює", callback_data="how_it_works")
    kb = with_support_button(kb)
    kb.adjust(1)

    await message.answer(
        f"🇺🇦 *Зарплата Щодня*\n"
        f"{divider()}\n\n"
        f"Привіт, {name}! 👋\n\n"
        f"Тут все просто: банки і сервіси платять бонуси новим "
        f"клієнтам — ми збираємо найкращі пропозиції в одному місці.\n\n"
        f"{divider()}\n\n"
        f"💰 *Що тут є:*\n\n"
        f"🏦 *Банки та картки*\n"
        f"Відкрий картку — отримай 100-400 грн на рахунок. "
        f"Без прихованих умов, без підписок.\n\n"
        f"₿ *Крипто-біржі*\n"
        f"Зареєструйся на біржі — отримай бонус до $50. "
        f"Верифікація через Дію — займає 5 хвилин.\n\n"
        f"💳 *Вигідні кредити*\n"
        f"Потрібні гроші? Підберемо кредит з найнижчою ставкою "
        f"від перевірених МФО. Без прихованих комісій.\n\n"
        f"{divider()}\n\n"
        f"❓ *Як це працює:*\n"
        f"Ти реєструєшся за нашим посиланням → банк або сервіс "
        f"платить нам за нового клієнта → ти отримуєш бонус. "
        f"Всі у плюсі. Жодного підступу.\n\n"
        f"{divider()}\n\n"
        f"🆘 Якщо щось незрозуміло — натисни «Підтримка» "
        f"в будь-який момент, я поясню кожен крок.\n\n"
        f"Гроші на карту. Швидко. Чесно. 💳",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "how_it_works")
async def how_it_works(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Почати заробляти!", callback_data="choose_category")
    kb.button(text="◀️ Назад", callback_data="back_start")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"ℹ️ *Як це працює*\n"
        f"{divider()}\n\n"
        f"*1.* Обираєш категорію 📂\n"
        f"*2.* Обираєш рівень складності ⚡\n"
        f"*3.* Виконуєш завдання 📋\n"
        f"*4.* Отримуєш гроші на картку 💰\n\n"
        f"{divider()}\n\n"
        f"🟢 *ЛЕГКО* — 5-15 хв → 50-200 грн\n"
        f"🟡 *СЕРЕДНЬО* — 15-30 хв → 200-500 грн\n"
        f"🔴 *ХАРД* — 30-60 хв → 500-2000 грн\n\n"
        f"{divider()}\n\n"
        f"✅ Всі офери офіційні\n"
        f"✅ Гроші приходять на картку\n"
        f"✅ Прогрес зберігається\n"
        f"✅ Можна зупинитись і продовжити",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# ═══════════════════════════════════════════
# ВИБІР КАТЕГОРІЇ ТА РІВНЯ
# ═══════════════════════════════════════════

@router.callback_query(F.data == "choose_category")
async def choose_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestState.selecting_category)

    kb = InlineKeyboardBuilder()
    kb.button(text="🏦 Банки та картки", callback_data="cat_banks")
    kb.button(text="₿ Крипто-біржі", callback_data="cat_crypto")
    kb.button(text="🔥 Все та одразу — MAX заробіток", callback_data="cat_all")
    kb.button(text="◀️ Назад", callback_data="back_start")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"💼 *Обери категорію*\n"
        f"{divider()}\n\n"
        f"🏦 *Банки та картки*\n"
        f"┗ Відкрий картку → отримай бонус\n\n"
        f"₿ *Крипто-біржі*\n"
        f"┗ Зареєструйся → верифікуйся → заробляй\n\n"
        f"🔥 *Все та одразу*\n"
        f"┗ Максимальний заробіток за один квест\n\n"
        f"{divider()}",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("cat_"))
async def choose_level(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    await state.update_data(category=cat)
    await state.set_state(QuestState.selecting_level)

    cat_names = {
        "banks": "🏦 Банки та картки",
        "crypto": "₿ Крипто-біржі",
        "all": "🔥 Все та одразу"
    }

    kb = InlineKeyboardBuilder()
    kb.button(text="🟢 ЛЕГКО — 50-200 грн │ 5-15 хв", callback_data="lvl_easy")
    kb.button(text="🟡 СЕРЕДНЬО — 200-500 грн │ 15-30 хв", callback_data="lvl_medium")
    kb.button(text="🔴 ХАРД — 500-2000 грн │ 30-60 хв", callback_data="lvl_hard")
    kb.button(text="◀️ Назад", callback_data="choose_category")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"⚡ *Обери рівень складності*\n"
        f"{divider()}\n\n"
        f"Категорія: {cat_names.get(cat, cat)}\n\n"
        f"🟢 *ЛЕГКО*\n"
        f"┣ Час: 5-15 хвилин\n"
        f"┣ Дії: встановити додаток + реєстрація\n"
        f"┗ Заробіток: 50-200 грн\n\n"
        f"🟡 *СЕРЕДНЬО*\n"
        f"┣ Час: 15-30 хвилин\n"
        f"┣ Дії: реєстрація + верифікація + перша дія\n"
        f"┗ Заробіток: 200-500 грн\n\n"
        f"🔴 *ХАРД*\n"
        f"┣ Час: 30-60 хвилин\n"
        f"┣ Дії: повна верифікація + активні дії\n"
        f"┗ Заробіток: 500-2000 грн\n\n"
        f"{divider()}\n"
        f"_Чим складніше — тим більше грошей_ 💰",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("lvl_"))
async def select_existing(callback: CallbackQuery, state: FSMContext):
    level = callback.data.replace("lvl_", "")
    await state.update_data(level=level)
    await state.set_state(QuestState.selecting_banks)
    await state.update_data(selected=[])

    data = await state.get_data()
    cat = data.get("category", "all")
    offers_for_cat = {k: v for k, v in OFFERS.items() if cat == "all" or v.get("category") == cat}

    kb = InlineKeyboardBuilder()
    for key, offer in offers_for_cat.items():
        kb.button(text=f"⬜ {offer['emoji']} {offer['name']}", callback_data=f"toggle_{key}")
    kb.button(text="✅ Далі — показати мій квест", callback_data="banks_done")
    kb.button(text="◀️ Назад", callback_data="choose_category")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"🔍 *Де ти вже зареєстрований?*\n"
        f"{divider()}\n\n"
        f"Відміть де вже є акаунт — ми їх пропустимо "
        f"і покажемо тільки нові можливості.\n\n"
        f"_Ніде немає? Просто натисни_ ✅ _Далі_",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_bank(callback: CallbackQuery, state: FSMContext):
    bank = callback.data.replace("toggle_", "")
    data = await state.get_data()
    selected = data.get("selected", [])
    cat = data.get("category", "all")

    if bank in selected:
        selected.remove(bank)
    else:
        selected.append(bank)

    await state.update_data(selected=selected)
    offers_for_cat = {k: v for k, v in OFFERS.items() if cat == "all" or v.get("category") == cat}

    kb = InlineKeyboardBuilder()
    for key, offer in offers_for_cat.items():
        check = "☑️" if key in selected else "⬜"
        kb.button(text=f"{check} {offer['emoji']} {offer['name']}", callback_data=f"toggle_{key}")
    kb.button(text="✅ Далі — показати мій квест", callback_data="banks_done")
    kb.button(text="◀️ Назад", callback_data="choose_category")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_reply_markup(reply_markup=kb.as_markup())

@router.callback_query(F.data == "banks_done")
async def show_quest(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected", [])
    level = data.get("level", "easy")
    cat = data.get("category", "all")

    await update_user(callback.from_user.id, "registered_banks", json.dumps(selected))

    offers_for_cat = {k: v for k, v in OFFERS.items() if cat == "all" or v.get("category") == cat}
    available_raw = [(k, v) for k, v in offers_for_cat.items() if k not in selected]

    level_map = {"easy": 1, "medium": 2, "hard": 3}
    lvl_num = level_map.get(level, 1)
    available = [(k, v) for k, v in available_raw if v.get("level", 1) <= lvl_num]
    available.sort(key=lambda x: x[1]["bonus"], reverse=True)

    if not available:
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Обрати іншу категорію", callback_data="choose_category")
        kb = with_support_button(kb)
        await callback.message.edit_text(
            f"😮 *Немає нових офферів*\n"
            f"{divider()}\n\n"
            f"Ти вже зареєстрований скрізь!\n"
            f"Спробуй іншу категорію або рівень.",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        return

    total = sum(v["bonus"] for _, v in available)
    progress = json.dumps({
        "current": 0,
        "completed": [],
        "available": [k for k, _ in available],
        "level": level,
        "category": cat
    })
    await update_user(callback.from_user.id, "quest_progress", progress)
    await state.set_state(QuestState.in_quest)

    level_badges = {"easy": "🟢 ЛЕГКО", "medium": "🟡 СЕРЕДНЬО", "hard": "🔴 ХАРД"}
    cat_names = {"banks": "🏦 Банки", "crypto": "₿ Крипто", "all": "🔥 Все"}

    text = (
        f"🎯 *Твій квест готовий!*\n"
        f"{divider()}\n\n"
        f"📂 {cat_names.get(cat, cat)} │ {level_badges.get(level, level)}\n\n"
    )

    for i, (key, offer) in enumerate(available, 1):
        text += f"*{i}.* {offer['emoji']} {offer['name']}\n"
        text += f"   💰 {offer['bonus_text']} │ ⏱ {offer['time']}\n\n"

    text += (
        f"{divider()}\n"
        f"💵 *Загалом: {total} грн*\n"
        f"⏰ ~{len(available) * 10} хвилин\n\n"
        f"{progress_bar(0, total)}\n\n"
        f"_Починаємо? Перший крок найлегший!_ 💪"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text=f"▶️ Крок 1: {available[0][1]['name']}", callback_data=f"step_{available[0][0]}")
    kb.button(text="🕐 Нагадати пізніше", callback_data="pause_quest")
    kb.button(text="◀️ Назад", callback_data="choose_category")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ═══════════════════════════════════════════
# ВИКОНАННЯ КРОКУ
# ═══════════════════════════════════════════

@router.callback_query(F.data.startswith("step_"))
async def show_step(callback: CallbackQuery):
    bank_key = callback.data.replace("step_", "")
    offer = OFFERS.get(bank_key)
    if not offer:
        return

    conditions = ""
    for i, c in enumerate(offer["conditions"], 1):
        conditions += f"   *{i}.* {c}\n"

    level_badges = {1: "🟢 ЛЕГКО", 2: "🟡 СЕРЕДНЬО", 3: "🔴 ХАРД"}

    kb = InlineKeyboardBuilder()
    kb.button(text="👉 Перейти за посиланням", url=offer["link"])
    kb.button(text="✅ Виконав — зараховуй!", callback_data=f"done_{bank_key}")
    kb.button(text="❓ Не виходить — допоможи", callback_data=f"help_{bank_key}")
    kb.button(text="⏸ Зупинитись на сьогодні", callback_data="pause_quest")
    kb.button(text="◀️ Назад", callback_data="back_start")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"{offer['emoji']} *{offer['name']}*\n"
        f"{divider()}\n\n"
        f"💰 Бонус: *{offer['bonus_text']}*\n"
        f"⏱ Час: {offer['time']}\n"
        f"⚡ Рівень: {level_badges.get(offer.get('level', 1))}\n"
        f"⭐ Оцінка: {offer['rating']}\n\n"
        f"{divider()}\n\n"
        f"📋 *Що потрібно зробити:*\n"
        f"{conditions}\n"
        f"⚠️ _{offer['note']}_\n\n"
        f"{divider()}\n\n"
        f"*1.* Натисни «Перейти за посиланням» 👇\n"
        f"*2.* Виконай всі кроки\n"
        f"*3.* Повернись і натисни ✅",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("done_"))
async def step_done(callback: CallbackQuery):
    bank_key = callback.data.replace("done_", "")
    offer = OFFERS.get(bank_key)
    user = await get_user(callback.from_user.id)

    progress = json.loads(user[3]) if user and user[3] else {}
    completed = progress.get("completed", [])
    available = progress.get("available", [])

    if bank_key not in completed:
        completed.append(bank_key)

    current = sum(OFFERS[k]["bonus"] for k in completed if k in OFFERS)
    total = sum(OFFERS[k]["bonus"] for k in available if k in OFFERS)

    progress["completed"] = completed
    progress["current"] = current
    await update_user(callback.from_user.id, "quest_progress", json.dumps(progress))
    await update_user(callback.from_user.id, "total_earned", current)

    remaining = [k for k in available if k not in completed]

    if not remaining:
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Новий квест", callback_data="choose_category")
        kb.button(text="📊 Мій прогрес", callback_data="my_progress")
        kb.button(text="◀️ Назад", callback_data="back_start")
        kb = with_support_button(kb)
        kb.adjust(1)

        await callback.message.edit_text(
            f"🏆 *КВЕСТ ЗАВЕРШЕНО!*\n"
            f"{divider()}\n\n"
            f"Ти зробив це! Так тримати! 🎉\n\n"
            f"💰 Зароблено: *{current} грн*\n\n"
            f"{progress_bar(current, total)}\n\n"
            f"{divider()}\n\n"
            f"📲 Бонуси надходять протягом 1-3 днів\n"
            f"🔔 Щопонеділка — нові офери!\n\n"
            f"Підпишись: @zarplata_shchodnya",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        return

    next_key = remaining[0]
    next_offer = OFFERS[next_key]

    kb = InlineKeyboardBuilder()
    kb.button(text=f"▶️ Крок {len(completed)+1}: {next_offer['name']}", callback_data=f"step_{next_key}")
    kb.button(text="⏸ Продовжити завтра", callback_data="pause_quest")
    kb.button(text="◀️ Назад", callback_data="back_start")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"✅ *+{offer['bonus_text']} зараховано!*\n"
        f"{divider()}\n\n"
        f"Чудово! Продовжуй у тому ж дусі 💪\n\n"
        f"💰 *{current}* з *{total} грн*\n"
        f"{progress_bar(current, total)}\n\n"
        f"{divider()}\n\n"
        f"⏭ Наступний: {next_offer['emoji']} *{next_offer['name']}*\n"
        f"💵 {next_offer['bonus_text']} │ ⏱ {next_offer['time']}\n\n"
        f"Продовжуємо? 👇",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# ═══════════════════════════════════════════
# ДОПОМОГА (швидкі кнопки під кожен крок)
# ═══════════════════════════════════════════

@router.callback_query(F.data.startswith("help_"))
async def help_router(callback: CallbackQuery):
    data = callback.data

    if data.startswith("help_install_"):
        bank_key = data.replace("help_install_", "")
        offer = OFFERS.get(bank_key, {})
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Встановив!", callback_data=f"step_{bank_key}")
        kb.button(text="😕 Все одно не виходить", callback_data=f"help_{bank_key}")
        kb.button(text="◀️ Назад", callback_data="back_start")
        kb = with_support_button(kb)
        kb.adjust(1)
        await callback.message.edit_text(
            f"📲 *Як встановити {offer.get('name', '')}*\n"
            f"{divider()}\n\n"
            f"*iPhone:*\n"
            f"1️⃣ Відкрий App Store\n"
            f"2️⃣ Введи назву в пошуку\n"
            f"3️⃣ Натисни «Завантажити»\n\n"
            f"*Android:*\n"
            f"1️⃣ Відкрий Google Play\n"
            f"2️⃣ Введи назву в пошуку\n"
            f"3️⃣ Натисни «Встановити»\n\n"
            f"💡 _Не знайшов? Спробуй повну назву_",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        return

    if data.startswith("help_verify_"):
        bank_key = data.replace("help_verify_", "")
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Верифікувався!", callback_data=f"step_{bank_key}")
        kb.button(text="😕 Ще є питання", callback_data=f"help_{bank_key}")
        kb.button(text="◀️ Назад", callback_data="back_start")
        kb = with_support_button(kb)
        kb.adjust(1)
        await callback.message.edit_text(
            f"🪪 *Верифікація — покроково*\n"
            f"{divider()}\n\n"
            f"*Через Дію (найшвидше):*\n"
            f"1️⃣ Переконайся що Дія встановлена\n"
            f"2️⃣ В банку обери «Верифікація через Дію»\n"
            f"3️⃣ Підтверди доступ\n"
            f"⏱ 2-3 хвилини ✅\n\n"
            f"*Через фото:*\n"
            f"1️⃣ Фото паспорта\n"
            f"2️⃣ Селфі з паспортом\n"
            f"3️⃣ Завантаж в додаток\n"
            f"⏱ 5-10 хвилин",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        return

    if data.startswith("help_card_"):
        bank_key = data.replace("help_card_", "")
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Оформив!", callback_data=f"step_{bank_key}")
        kb.button(text="😕 Ще є питання", callback_data=f"help_{bank_key}")
        kb.button(text="◀️ Назад", callback_data="back_start")
        kb = with_support_button(kb)
        kb.adjust(1)
        await callback.message.edit_text(
            f"💳 *Як оформити картку*\n"
            f"{divider()}\n\n"
            f"1️⃣ Розділ «Картки» в додатку\n"
            f"2️⃣ «Замовити картку» або «Відкрити»\n"
            f"3️⃣ Обери з кредитним лімітом — більший бонус\n"
            f"4️⃣ Підтверди замовлення\n\n"
            f"⚠️ _Кредитний ліміт — безкоштовно_\n"
            f"💡 _Відмовили? Картка без ліміту теж дає бонус_",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        return

    bank_key = data.replace("help_", "")
    offer = OFFERS.get(bank_key, {})
    kb = InlineKeyboardBuilder()
    kb.button(text="📲 Не можу встановити додаток", callback_data=f"help_install_{bank_key}")
    kb.button(text="🪪 Проблема з верифікацією", callback_data=f"help_verify_{bank_key}")
    kb.button(text="💳 Не можу оформити картку", callback_data=f"help_card_{bank_key}")
    kb.button(text="🤖 Інше питання — спитати AI", callback_data="open_support")
    kb.button(text="◀️ Назад до кроку", callback_data=f"step_{bank_key}")
    kb.adjust(1)
    await callback.message.edit_text(
        f"🆘 *Допомога: {offer.get('name', '')}*\n"
        f"{divider()}\n\n"
        f"Що саме не виходить?\n"
        f"Обери проблему — поясню покроково 👇",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# ═══════════════════════════════════════════
# AI ПІДТРИМКА
# ═══════════════════════════════════════════

@router.callback_query(F.data == "open_support")
async def open_support(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestState.asking_support)

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Скасувати", callback_data="back_start")

    await callback.message.edit_text(
        f"🤖 *AI-Підтримка*\n"
        f"{divider()}\n\n"
        f"Привіт! Я можу відповісти на будь-яке питання "
        f"про бонуси, верифікацію, картки, крипто-біржі чи кредити.\n\n"
        f"Просто напиши своє питання текстом 👇\n\n"
        f"_Якщо я не зможу допомогти — передам адміністратору_",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.message(QuestState.asking_support)
async def handle_support_question(message: Message, state: FSMContext, bot: Bot):
    user_name = message.from_user.first_name or "Користувач"
    username = message.from_user.username or ""
    user_id = message.from_user.id

    thinking_msg = await message.answer("🤖 _Думаю над відповіддю..._", parse_mode="Markdown")

    answer, escalate = await ask_ai(message.text, user_name)

    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Ще питання", callback_data="open_support")
    kb.button(text="🏠 Головне меню", callback_data="back_start")
    kb.adjust(1)

    await thinking_msg.edit_text(
        f"🤖 *AI-Підтримка*\n"
        f"{divider()}\n\n"
        f"{answer}",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

    if escalate:
        await notify_admin(bot, user_id, user_name, username, message.text)

# ═══════════════════════════════════════════
# ПАУЗА І НАГАДУВАННЯ
# ═══════════════════════════════════════════

@router.callback_query(F.data == "pause_quest")
async def pause_quest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestState.waiting_reminder)
    user = await get_user(callback.from_user.id)
    progress = json.loads(user[3]) if user and user[3] else {}
    completed = progress.get("completed", [])
    available = progress.get("available", [])
    current = sum(OFFERS[k]["bonus"] for k in completed if k in OFFERS)
    total = sum(OFFERS[k]["bonus"] for k in available if k in OFFERS)

    kb = InlineKeyboardBuilder()
    for t in ["9:00", "12:00", "18:00", "20:00"]:
        kb.button(text=f"🕐 {t}", callback_data=f"remind_{t}")
    kb.button(text="🚫 Не нагадувати", callback_data="no_remind")
    kb.adjust(2, 2, 1)

    await callback.message.edit_text(
        f"⏸ *Зупиняємось*\n"
        f"{divider()}\n\n"
        f"Прогрес збережено 💾\n\n"
        f"💰 *{current}* з *{total} грн*\n"
        f"{progress_bar(current, total)}\n\n"
        f"{divider()}\n\n"
        f"🔔 О котрій нагадати завтра?",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("remind_"))
async def set_reminder(callback: CallbackQuery, state: FSMContext):
    time = callback.data.replace("remind_", "")
    await update_user(callback.from_user.id, "reminder_time", time)
    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Головне меню", callback_data="back_start")

    await callback.message.edit_text(
        f"✅ *Нагадування встановлено*\n"
        f"{divider()}\n\n"
        f"Нагадаю завтра о *{time}* ⏰\n\n"
        f"Підпишись на канал — там нові офери щодня:\n"
        f"👉 @zarplata_shchodnya",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "no_remind")
async def no_reminder(callback: CallbackQuery, state: FSMContext):
    await update_user(callback.from_user.id, "reminder_time", None)
    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Головне меню", callback_data="back_start")

    await callback.message.edit_text(
        f"👌 *Зрозумів*\n"
        f"{divider()}\n\n"
        f"Прогрес збережено 💾\n"
        f"Напиши /start коли будеш готовий 💪",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# ═══════════════════════════════════════════
# МІЙ ПРОГРЕС
# ═══════════════════════════════════════════

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    total_earned = user[6] if user else 0
    progress = json.loads(user[3]) if user and user[3] else {}
    completed = progress.get("completed", [])
    available = progress.get("available", [])
    current = sum(OFFERS[k]["bonus"] for k in completed if k in OFFERS)
    total = sum(OFFERS[k]["bonus"] for k in available if k in OFFERS)

    completed_text = ""
    for key in completed:
        if key in OFFERS:
            completed_text += f"✅ {OFFERS[key]['emoji']} {OFFERS[key]['name']} — {OFFERS[key]['bonus_text']}\n"

    remaining = [k for k in available if k not in completed]
    remaining_text = ""
    for key in remaining:
        if key in OFFERS:
            remaining_text += f"⬜ {OFFERS[key]['emoji']} {OFFERS[key]['name']} — {OFFERS[key]['bonus_text']}\n"

    kb = InlineKeyboardBuilder()
    if remaining:
        kb.button(text="▶️ Продовжити квест", callback_data=f"step_{remaining[0]}")
    kb.button(text="🔄 Новий квест", callback_data="choose_category")
    kb.button(text="◀️ Назад", callback_data="back_start")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"📊 *Мій прогрес*\n"
        f"{divider()}\n\n"
        f"💰 Всього зароблено: *{total_earned} грн*\n\n"
        f"{progress_bar(current, total)}\n"
        f"*{current}* з *{total} грн*\n\n"
        f"{divider()}\n\n"
        f"{'✅ *Виконано:*' + chr(10) + completed_text + chr(10) if completed_text else ''}"
        f"{'⬜ *Залишилось:*' + chr(10) + remaining_text if remaining_text else ''}",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# ═══════════════════════════════════════════
# НАВІГАЦІЯ
# ═══════════════════════════════════════════

@router.callback_query(F.data == "back_start")
async def back_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    name = callback.from_user.first_name or "друже"

    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Почати заробляти", callback_data="choose_category")
    kb.button(text="📊 Мій прогрес", callback_data="my_progress")
    kb.button(text="ℹ️ Як це працює", callback_data="how_it_works")
    kb = with_support_button(kb)
    kb.adjust(1)

    await callback.message.edit_text(
        f"🇺🇦 *Зарплата Щодня*\n"
        f"{divider()}\n\n"
        f"Привіт, {name}! 👋\n\n"
        f"Тут все просто: банки і сервіси платять бонуси новим "
        f"клієнтам — ми збираємо найкращі пропозиції в одному місці.\n\n"
        f"{divider()}\n\n"
        f"💰 *Що тут є:*\n\n"
        f"🏦 *Банки та картки* — до 400 грн\n"
        f"₿ *Крипто-біржі* — до $50\n"
        f"💳 *Вигідні кредити* — найнижчі ставки\n\n"
        f"_Без інвестицій. Без ризиків. Гроші на картку._\n\n"
        f"{divider()}",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
