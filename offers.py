OFFERS = {
    "obank": {
        "name": "O.Bank",
        "emoji": "🟢",
        "bonus": 400,
        "bonus_text": "400 грн",
        "time": "15 хв",
        "difficulty": "Середня",
        "conditions": [
            "Встанови додаток O.Bank",
            "Оформи О.Картку+",
            "Зроби покупку від 500 грн протягом місяця"
        ],
        "note": "Без кредитного ліміту — бонус 200 грн",
        "link": "https://ideabank.ua/uk/referalna-programa",  # замінити на свій реф. лінк
        "rating": "9/10"
    },
    "pumb": {
        "name": "ПУМБ",
        "emoji": "🟡",
        "bonus": 300,
        "bonus_text": "300 грн",
        "time": "10 хв",
        "difficulty": "Легка",
        "conditions": [
            "Встанови додаток ПУМБ за посиланням",
            "Відкрий картку з кредитним лімітом",
            "Оплати будь-що від 100 грн"
        ],
        "note": "Без кредитного ліміту — бонус 100 грн",
        "link": "https://pumb.onelink.me/Jrxy/dr0o3xxh",  # замінити на свій реф. лінк
        "rating": "8/10"
    },
    "privat": {
        "name": "ПриватБанк",
        "emoji": "🟢",
        "bonus": 150,
        "bonus_text": "150 грн",
        "time": "5 хв",
        "difficulty": "Легка",
        "conditions": [
            "Перейди за посиланням",
            "Оформи картку Універсальна",
            "Активуй картку"
        ],
        "note": "Лише для нових клієнтів ПриватБанку",
        "link": "https://www.privat24.ua/invite/4b8kd",  # замінити на свій реф. лінк
        "rating": "8/10"
    },
    "mono": {
        "name": "Monobank",
        "emoji": "⚫",
        "bonus": 100,
        "bonus_text": "100 грн",
        "time": "5 хв",
        "difficulty": "Легка",
        "conditions": [
            "Перейди за посиланням",
            "Відкрий кредитну картку",
            "Активуй картку"
        ],
        "note": "Лише для нових клієнтів від 18 років",
        "link": "https://mono.ua/r/YOUR_REF",  # замінити на свій реф. лінк
        "rating": "7/10"
    },
    "sense": {
        "name": "Sense Bank",
        "emoji": "🔵",
        "bonus": 100,
        "bonus_text": "100 грн",
        "time": "5 хв",
        "difficulty": "Легка",
        "conditions": [
            "Завантаж додаток Sense Bank",
            "Зареєструйся за реф. посиланням",
            "Верифікуйся через Дію"
        ],
        "note": "Бонус отримують обидві сторони",
        "link": "https://sensebank.com.ua/?ref=YOUR_REF",  # замінити на свій реф. лінк
        "rating": "7/10"
    },
    "taskom": {
        "name": "ТАСКОМБАНК",
        "emoji": "🏦",
        "bonus": 100,
        "bonus_text": "100 грн",
        "time": "5 хв",
        "difficulty": "Легка",
        "conditions": [
            "Зареєструйся за посиланням",
            "Відкрий будь-яку картку",
            "Зроби першу операцію"
        ],
        "note": "1.5% кешбек на продукти в подарунок",
        "link": "https://tascombank.ua/?ref=YOUR_REF",  # замінити на свій реф. лінк
        "rating": "7/10"
    }
}

BANK_NAMES = {
    "obank": "O.Bank",
    "pumb": "ПУМБ",
    "privat": "ПриватБанк",
    "mono": "Monobank",
    "sense": "Sense Bank",
    "taskom": "ТАСКОМБАНК"
}

def get_available_offers(registered_banks: list) -> list:
    """Повертає офери для банків де людина ще не зареєстрована"""
    available = []
    for key, offer in OFFERS.items():
        if key not in registered_banks:
            available.append((key, offer))
    # Сортуємо за розміром бонусу
    available.sort(key=lambda x: x[1]["bonus"], reverse=True)
    return available

def calculate_total(available_offers: list) -> int:
    """Рахує загальну суму доступних бонусів"""
    return sum(offer["bonus"] for _, offer in available_offers)
