import requests

TOKEN = "bot522634:1dfaab0d-da5a-4b6a-8793-bad5b718ee21"
CHAT_ID = "11248933"

def send_news(title, text, source="منبع آزمایشی"):
    message = f"""🚨 نبض روز | خبر فوری

📰 {title}

{text}

━━━━━━━━━━━━
📌 منبع: {source}
⚡ نبض روز | خبر و قیمت
"""

    url = f"https://eitaayar.ir/api/{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print("Status:", response.status_code)
    print("Response:", response.text)


send_news(
    "آغاز فعالیت آزمایشی نبض روز",
    "سیستم انتشار خودکار با موفقیت راه‌اندازی شد. ✅"
)