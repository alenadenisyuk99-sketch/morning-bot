import urllib.request, json, os, re, datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
ALONA_CHAT_ID = 5112530455

CHANNELS = [
    "you_can_know_more","besidamedia","marketing_ukr","gravmarketing",
    "Kukurudza_blog","BrainHubbb","target_pane","cozymarketingua",
    "TakTceClear","marketolog_ukr","JenyaSegeda","digitalnia",
    "utpumene","mflg_agency","umarketer","creativeness_marketing"
]

def fetch_channel(ch):
    try:
        req = urllib.request.Request(
            f"https://t.me/s/{ch}",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
        posts = re.findall(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        clean = [re.sub(r'<[^>]+>', "", p).strip() for p in posts[-3:]]
        return [p for p in clean if len(p) > 60]
    except:
        return []

def claude(prompt):
    data = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2500,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={"Content-Type": "application/json", "x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["content"][0]["text"]

def send(text):
    data = json.dumps({"chat_id": ALONA_CHAT_ID, "text": text, "disable_web_page_preview": True}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data=data, headers={"Content-Type": "application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

print("Fetching channels...")
all_posts = []
for ch in CHANNELS:
    posts = fetch_channel(ch)
    for p in posts:
        all_posts.append(f"[{ch}] {p[:400]}")
    print(f"  {ch}: {len(posts)} posts")

if not all_posts:
    send("Канали мовчать сьогодні \U0001F92B Повернусь завтра.")
    exit()

today = datetime.date.today().strftime("%d.%m.%Y")
posts_text = "\n---\n".join(all_posts[:40])

digest_text = claude(f"""Ти — ранковий дайджест для Альони Денисюк, CMO "Мережа Права". Вона будує особистий бренд у LinkedIn.

Сьогодні {today}. Ось свіжі пости з Telegram-каналів:

{posts_text}

Вибери 5-7 найцікавіших для LinkedIn. Пріоритет: маркетинг-інсайти, AI-тренди, кейси, практичні поради, статистика. Ігноруй рекламу і самопіар.

Напиши дайджест українською (до 3500 символів):
Доброго ранку! Ось що цікавого для LinkedIn сьогодні:

1. [Назва теми]
[2-3 речення]
https://t.me/channelname

...""")

print("Sending digest...")
if len(digest_text) > 3800:
    mid = digest_text.rfind("\n", 0, 3800 // 2)
    send(digest_text[:mid])
    send(digest_text[mid:])
else:
    send(digest_text)
print("Done!")
