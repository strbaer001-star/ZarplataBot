OFFERS = {
    "obank": {
        "name": "O.Bank",
        "emoji": "🟢",
        "bonus": 400,
        "bonus_text": "400 грн",
        "time": "15 хв",
        "level": 2,
        "category": "banks",
        "conditions": [
            "Встанови додаток O.Bank за посиланням",
            "Оформи О.Картку+",
            "Зроби покупку від 500 грн протягом місяця"
        ],
        "note": "Без кредитного ліміту — бонус 200 грн",
        "link": "https://ideabank.ua/uk/referalna-programa",
        "rating": "9/10 ⭐"
    },
    "pumb": {
        "name": "ПУМБ",
        "emoji": "🟡",
        "bonus": 300,
        "bonus_text": "300 грн",
        "time": "10 хв",
        "level": 2,
        "category": "banks",
        "conditions": [
            "Встанови додаток ПУМБ за посиланням",
            "Відкрий картку з кредитним лімітом",
            "Оплати будь-що від 100 грн"
        ],
        "note": "Без кредитного ліміту — бонус 100 грн",
        "link": "https://pumb.onelink.me/Jrxy/dr0o3xxh",
        "rating": "8/10 ⭐"
    },
    "privat": {
        "name": "ПриватБанк",
        "emoji": "🟢",
        "bonus": 150,
        "bonus_text": "150 грн",
        "time": "5 хв",
        "level": 1,
        "category": "banks",
        "conditions": [
            "Перейди за посиланням",
            "Оформи картку Універсальна",
            "Активуй картку"
        ],
        "note": "Лише для нових клієнтів ПриватБанку",
        "link": "https://www.privat24.ua/invite/4b8kd",
        "rating": "8/10 ⭐"
    },
    "mono": {
        "name": "Monobank",
        "emoji": "⚫",
        "bonus": 100,
        "bonus_text": "100 грн",
        "time": "5 хв",
        "level": 1,
        "category": "banks",
        "conditions": [
            "Перейди за посиланням",
            "Відкрий кредитну картку",
            "Активуй картку"
        ],
        "note": "Лише для нових клієнтів від 18 років",
        "link": "https://mono.ua/r/YOUR_REF",
        "rating": "7/10 ⭐"
    },
    "sense": {
        "name": "Sense Bank",
        "emoji": "🔵",
        "bonus": 100,
        "bonus_text": "100 грн",
        "time": "5 хв",
        "level": 1,
        "category": "banks",
        "conditions": [
            "Завантаж додаток Sense Bank",
            "Зареєструйся за посиланням",
            "Верифікуйся через Дію"
        ],
        "note": "Бонус отримують обидві сторони",
        "link": "https://sensebank.com.ua/?ref=YOUR_REF",
        "rating": "7/10 ⭐"
    },
    "binance": {
        "name": "Binance",
        "emoji": "🟡",
        "bonus": 1200,
        "bonus_text": "~$30 (≈1200 грн)",
        "time": "20 хв",
        "level": 2,
        "category": "crypto",
        "conditions": [
            "Зареєструйся за посиланням",
            "Пройди верифікацію KYC",
            "Поповни рахунок від $50"
        ],
        "note": "Бонус залежить від суми депозиту",
        "link": "https://www.binance.com/en/register?ref=YOUR_REF",
        "rating": "9/10 ⭐"
    },
    "bybit": {
        "name": "Bybit",
        "emoji": "🟠",
        "bonus": 1000,
        "bonus_text": "~$25 (≈1000 грн)",
        "time": "20 хв",
        "level": 2,
        "category": "crypto",
        "conditions": [
            "Зареєструйся за посиланням",
            "Пройди верифікацію",
            "Поповни рахунок від $100"
        ],
        "note": "Бонус приходить протягом 7 днів",
        "link": "https://www.bybit.com/en/register?affiliate_id=YOUR_REF",
        "rating": "8/10 ⭐"
    },
    "kuna": {
        "name": "Kuna",
        "emoji": "🇺🇦",
        "bonus": 400,
        "bonus_text": "~$10 (≈400 грн)",
        "time": "15 хв",
        "level": 1,
        "category": "crypto",
        "conditions": [
            "Зареєструйся за посиланням",
            "Верифікуйся через Дію",
            "Зроби першу транзакцію"
        ],
        "note": "Українська біржа — верифікація через Дію",
        "link": "https://kuna.io/?ref=YOUR_REF",
        "rating": "7/10 ⭐"
    }
}

def get_available_offers(registered: list) -> list:
    available = []
    for key, offer in OFFERS.items():
        if key not in registered:
            available.append((key, offer))
    available.sort(key=lambda x: x[1]["bonus"], reverse=True)
    return available

def calculate_total(offers: list) -> int:
    return sum(o["bonus"] for _, o in offers)
