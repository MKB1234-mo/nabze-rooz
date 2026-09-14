import requests
import xml.etree.ElementTree as ET
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# =========================
# تنظیمات
# =========================

TOKEN = "bot522634:35556003-1297-40a7-b819-38ae5f9740b8"

CHAT_ID = "11248933"

CHANNEL_USERNAME = "@nabzrooz_news"

LAST_NEWS_FILE = "last_news.txt"


RSS_FEEDS = [
    {
        "name": "تسنیم",
        "url": "https://www.tasnimnews.ir/fa/rss/feed/0/0/8/1/TopStories"
    },
    {
        "name": "مهر",
        "url": "https://www.mehrnews.com/rss"
    }
]


# =========================
# کلمات مهم
# =========================

IMPORTANT_WORDS = [
    "فوری",
    "هشدار",
    "زلزله",
    "سیل",
    "سیلاب",
    "هواشناسی",
    "بارندگی",
    "تصادف",
    "حادثه",
    "انفجار",
    "آتش‌سوزی",
    "دلار",
    "طلا",
    "سکه",
    "بورس",
    "اقتصاد",
    "دولت",
    "مجلس",
    "رئیس جمهور",
    "انتخابات",
    "جنگ",
    "حمله",
    "ورزش",
    "فوتبال",
    "والیبال",
    "بسکتبال",
    "تیم ملی",
    "ایران",
    "آمریکا",
    "اسرائیل"
]


# =========================
# خبرهای قبلی
# =========================

sent_links = set()

if os.path.exists(LAST_NEWS_FILE):

    with open(
        LAST_NEWS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        sent_links = set(
            line.strip()
            for line in f
            if line.strip()
        )


# =========================
# دریافت RSS
# =========================

all_news = []

for feed in RSS_FEEDS:

    try:

        response = requests.get(
            feed["url"],
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        print(
            feed["name"],
            "RSS Status:",
            response.status_code
        )

        if response.status_code != 200:
            continue

        root = ET.fromstring(
            response.content
        )

        for item in root.findall(".//item")[:10]:

            title = item.findtext(
                "title"
            ) or ""

            link = item.findtext(
                "link"
            ) or ""

            if not title or not link:
                continue

            all_news.append({
                "title": title.strip(),
                "link": link.strip(),
                "source": feed["name"]
            })

    except Exception as e:

        print(
            "RSS Error:",
            e
        )


# =========================
# انتخاب خبر جدید و مهم
# =========================

new_news = None

for item in all_news:

    if item["link"] in sent_links:
        continue

    title_lower = item["title"].lower()

    score = 0

    for word in IMPORTANT_WORDS:

        if word.lower() in title_lower:
            score += 1

    if score >= 1:

        new_news = item
        break


# اگر خبری پیدا نشد
if not new_news:

    print(
        "❌ خبر جدید و مهمی پیدا نشد."
    )

    exit()


print()
print("📰 خبر انتخاب‌شده:")
print(new_news["title"])
print("🔗", new_news["link"])


# =========================
# دریافت صفحه خبر
# =========================

try:

    article_response = requests.get(
        new_news["link"],
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    print(
        "Article Status:",
        article_response.status_code
    )

except Exception as e:

    print(
        "Article Error:",
        e
    )

    exit()


# =========================
# پیدا کردن عکس خبر
# =========================

soup = BeautifulSoup(
    article_response.text,
    "html.parser"
)

image_url = None


# عکس اصلی خبر
og_image = soup.find(
    "meta",
    property="og:image"
)

if og_image and og_image.get("content"):

    image_url = og_image.get(
        "content"
    )


# اگر عکس اصلی نبود
if not image_url:

    twitter_image = soup.find(
        "meta",
        attrs={
            "name": "twitter:image"
        }
    )

    if twitter_image and twitter_image.get(
        "content"
    ):

        image_url = twitter_image.get(
            "content"
        )


# تبدیل لینک نسبی به کامل
if image_url:

    image_url = urljoin(
        new_news["link"],
        image_url
    )


print()
print("==============================")
print("🖼️ عکس:")
print(image_url)
print("==============================")


# =========================
# ساخت متن نهایی
# =========================

TEXT = f"""📰 {new_news["title"]}

🆔 {CHANNEL_USERNAME}"""


print()
print("==============================")
print(TEXT)
print("==============================")


# =========================
# آدرس API ایتایار
# =========================

BASE_URL = (
    f"https://eitaayar.ir/api/{TOKEN}"
)


# =========================
# اگر عکس وجود داشت
# =========================

if image_url:

    try:

        image_response = requests.get(
            image_url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        print(
            "Image Download Status:",
            image_response.status_code
        )


        if image_response.status_code == 200:

            image_file = "news_image.jpg"


            # ذخیره عکس
            with open(
                image_file,
                "wb"
            ) as f:

                f.write(
                    image_response.content
                )


            # ارسال عکس
            send_url = (
                BASE_URL +
                "/sendFile"
            )


            with open(
                image_file,
                "rb"
            ) as image:

                files = {
                    "file": (
                        "news_image.jpg",
                        image,
                        "image/jpeg"
                    )
                }

                data = {
                    "chat_id": CHAT_ID,
                    "caption": TEXT
                }


                eitaa_response = requests.post(
                    send_url,
                    files=files,
                    data=data,
                    timeout=60
                )


            print(
                "Eitaa Status:",
                eitaa_response.status_code
            )

            print(
                eitaa_response.text
            )


            # بررسی موفقیت
            try:

                result = eitaa_response.json()

                if result.get("ok"):

                    with open(
                        LAST_NEWS_FILE,
                        "a",
                        encoding="utf-8"
                    ) as f:

                        f.write(
                            new_news["link"] +
                            "\n"
                        )


                    print(
                        "✅ خبر و عکس با موفقیت ارسال شد."
                    )

                else:

                    print(
                        "❌ ارسال ناموفق بود."
                    )


            except Exception:

                print(
                    "⚠️ پاسخ ایتا قابل بررسی نبود."
                )


            # حذف عکس موقت
            if os.path.exists(
                image_file
            ):

                os.remove(
                    image_file
                )


        else:

            print(
                "❌ دانلود عکس ناموفق بود."
            )


    except Exception as e:

        print(
            "❌ خطا در ارسال عکس:"
        )

        print(e)


# =========================
# اگر عکس وجود نداشت
# =========================

else:

    print(
        "🖼️ عکس مرتبط پیدا نشد."
    )


    try:

        send_url = (
            BASE_URL +
            "/sendMessage"
        )


        data = {
            "chat_id": CHAT_ID,
            "text": TEXT
        }


        eitaa_response = requests.post(
            send_url,
            data=data,
            timeout=30
        )


        print(
            "Eitaa Status:",
            eitaa_response.status_code
        )

        print(
            eitaa_response.text
        )


        try:

            result = eitaa_response.json()

            if result.get("ok"):

                with open(
                    LAST_NEWS_FILE,
                    "a",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        new_news["link"] +
                        "\n"
                    )


                print(
                    "✅ خبر با موفقیت ارسال شد."
                )

        except Exception:

            pass


    except Exception as e:

        print(
            "❌ خطا در ارسال خبر:"
        )

        print(e)
