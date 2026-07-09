import urllib.request, json, os

token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = -1002879305150

data = json.dumps({"chat_id": chat_id, "text": "\U0001F921"}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=data,
    headers={"Content-Type": "application/json; charset=utf-8"}
)
with urllib.request.urlopen(req, timeout=15) as r:
    result = json.loads(r.read())
    print("Clown sent! message_id:", result["result"]["message_id"])
