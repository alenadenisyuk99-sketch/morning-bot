import urllib.request, json, os, datetime, random

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
CHAT_IDS = [-1002879305150, -1003988330017]  # Мережа Права + Маркетинг AGRIUM

def claude(prompt, max_tokens=2000):
    data = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={"Content-Type": "application/json", "x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["content"][0]["text"]

def gramotey(text):
    return claude(f"""Ти — Грамотєй, суворий редактор. Твоя задача — зробити текст живим і грамотним.

Що шукати і виправляти:

1. Русизми та суржик — будь-які російські слова ("да", "нет", "очень", "конечно" тощо). Замінити на природні українські.

2. Кальки з англійської або російської — фрази, перекладені дослівно і тому незрозумілі або штучні.
   Погано: "виявляються на дивовижний дух з вами" → Добре: "з якими тобі по дорозі"
   Погано: "зірки сприяють гармонії зв'язків" → Добре: "зателефонуй близьким сьогодні"

3. Незрозумілі конструкції — якщо речення незрозуміле або звучить як машинний переклад, переписати повністю простіше.

4. Вигадані слова, дивні фразеологізми, надмірний пафос.

Головне правило: краще просто і зрозуміло, ніж "красиво" але дивно. Якщо речення незрозуміле — переписуй його повністю живими словами, не намагайся виправити по словах.

Структуру і зміст не змінюй. Поверни лише виправлений текст, без коментарів.

ТЕКСТ:
{text}""", max_tokens=2500)

def send_text(text):
    for chat_id in CHAT_IDS:
        data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json; charset=utf-8"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            json.loads(r.read())

def send_photo(url, caption):
    for chat_id in CHAT_IDS:
        data = json.dumps({"chat_id": chat_id, "photo": url, "caption": caption}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data=data, headers={"Content-Type": "application/json; charset=utf-8"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            json.loads(r.read())

today = datetime.date.today()
day_of_year = today.timetuple().tm_yday

CARDS = [
    ("Дурень","RWS_Tarot_00_Fool.jpg"),("Маг","RWS_Tarot_01_Magician.jpg"),
    ("Велика Жриця","RWS_Tarot_02_High_Priestess.jpg"),("Імператриця","RWS_Tarot_03_Empress.jpg"),
    ("Імператор","RWS_Tarot_04_Emperor.jpg"),("Ієрофант","RWS_Tarot_05_Hierophant.jpg"),
    ("Закоханці","RWS_Tarot_06_Lovers.jpg"),("Колісниця","RWS_Tarot_07_Chariot.jpg"),
    ("Сила","RWS_Tarot_08_Strength.jpg"),("Відлюдник","RWS_Tarot_09_Hermit.jpg"),
    ("Колесо Фортуни","RWS_Tarot_10_Wheel_of_Fortune.jpg"),("Справедливість","RWS_Tarot_11_Justice.jpg"),
    ("Повішений","RWS_Tarot_12_Hanged_Man.jpg"),("Смерть","RWS_Tarot_13_Death.jpg"),
    ("Поміркованість","RWS_Tarot_14_Temperance.jpg"),("Диявол","RWS_Tarot_15_Devil.jpg"),
    ("Вежа","RWS_Tarot_16_Tower.jpg"),("Зірка","RWS_Tarot_17_Star.jpg"),
    ("Місяць","RWS_Tarot_18_Moon.jpg"),("Сонце","RWS_Tarot_19_Sun.jpg"),
    ("Суд","RWS_Tarot_20_Judgement.jpg"),("Світ","RWS_Tarot_21_World.jpg"),
]
card_name, card_file = CARDS[day_of_year % 22]
card_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{card_file}"

SPHERES = [
    "кохання та стосунки",
    "фінанси та гроші",
    "кар'єра та амбіції",
    "здоров'я та енергія",
    "родина та близькі",
    "творчість та натхнення",
    "дружба та соціум",
    "особистий розвиток та самопізнання",
    "відпочинок та відновлення",
    "комунікація та переговори",
    "інтуїція та внутрішній стан",
    "нові можливості та зміни",
]
random.seed(day_of_year * 7 + 13)
daily_spheres = SPHERES.copy()
random.shuffle(daily_spheres)

signs = [
    ("♈", "Овен"), ("♉", "Телець"), ("♊", "Близнюки"), ("♋", "Рак"),
    ("♌", "Лев"), ("♍", "Діва"), ("♎", "Терези"), ("♏", "Скорпіон"),
    ("♐", "Стрілець"), ("♑", "Козеріг"), ("♒", "Водолій"), ("♓", "Риби"),
]

# Сфери — тільки для Claude як інструкція, не з'являються в тексті
sphere_hints = "\n".join([
    f"{emoji} {name} → тема дня: {sphere}"
    for (emoji, name), sphere in zip(signs, daily_spheres)
])

horoscope_raw = claude(f"""Ти — астролог, який щодня пише гороскоп для живих людей у Telegram-чаті. Сьогодні {today.strftime("%d.%m.%Y")}.

Правила:
— Пиши так, як українець говорить з друзями — просто, природно, без пафосу. Не як переклад, не як книжка.
— Якщо не знаєш як сказати щось природно — скажи простіше. Краще "подзвони мамі" ніж незрозуміла метафора.
— Мова: грамотна українська. Жодного "да", "нет", русизмів, вигаданих слів.
— Стиль: теплий, трохи з гумором. Як пишуть популярні астрологи в Instagram.
— Обсяг: рівно 2 речення на кожен знак.
— Тема: кожен знак отримує підказку в різній сфері (вказано нижче). НЕ згадуй назву сфери у тексті.
— Конкретно і по-людськи: "зателефонуй мамі сьогодні" — добре. "Зірки сприяють гармонії сімейних зв'язків" — погано.
— Без стереотипів знаку зодіаку.

Теми на сьогодні (тільки для тебе, не виводь їх):
{sphere_hints}

Формат відповіді:
Доброго ранку, команда! Зорі сьогодні кажуть:

♈ Овен: [два речення]
♉ Телець: [два речення]
(і так далі для всіх 12 знаків)""")

print("=== HOROSCOPE RAW ===")
print(horoscope_raw)
print("=== ГРАМОТЄЙ CHECK ===")
horoscope_text = gramotey(horoscope_raw)
print(horoscope_text)
print("======================")

send_text(horoscope_text)
print("Horoscope sent!")

tarot_raw = claude(f"""Карта таро дня: {card_name}.
Напиши 3 речення грамотною літературною українською — тепло і природно, для людей що починають свій день.
Що ця карта несе сьогодні: яка енергія, що варто врахувати, який настрій. Темні карти — як виклик або трансформацію, без страшилок.
Жодного суржику і вигаданих слів — лише зрозуміла жива мова.
Починай з: 🃏 Карта дня: {card_name}""")

tarot_caption = gramotey(tarot_raw)

print("=== TAROT ===")
print(tarot_caption)
print("=============")
try:
    send_photo(card_url, tarot_caption)
except Exception as e:
    print(f"Photo failed ({e}), sending text")
    send_text(tarot_caption)
print("Done!")
