import asyncio
import logging
import feedparser
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from datetime import datetime

# بيانات البوت
TELEGRAM_BOT_TOKEN = "7679398911:AAHQC0Bhn9cMKKH0bgiDtfgg78SK4iFFHkA"
CHANNEL_ID = "@AnimPq_1"  # اسم القناة

# روابط RSS
RSS_FEEDS = [
    "https://www.animenewsnetwork.com/all/rss.xml",
    "https://myanimelist.net/rss/news.xml",
    "https://www.crunchyroll.com/rss/anime_news"
]

# إعداد البوت
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# لتفادي تكرار الروابط
sent_links = set()

# دالة الترجمة باستخدام LibreTranslate
async def translate_text(text):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "en",
        "target": "ar",
        "format": "text"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, data=payload, headers=headers)
            result = response.json()
            translated_text = result["translatedText"]
            return translated_text.strip()
    except Exception as e:
        print(f"خطأ أثناء الترجمة: {e}")
        return text  # لو فشلت الترجمة، يرجع النص الأصلي

# دالة جلب الأخبار وإرسالها
async def fetch_and_send_news():
    while True:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if entry.link not in sent_links:
                    title = entry.title
                    summary = entry.summary if 'summary' in entry else ''

                    translated_title = await translate_text(title)
                    translated_summary = await translate_text(summary)

                    message = f"<b>{translated_title}</b>\n\n{translated_summary}\n\nالمصدر: {entry.link}"
                    try:
                        await bot.send_message(CHANNEL_ID, message)
                        print(f"تم إرسال خبر: {translated_title}")
                        sent_links.add(entry.link)
                    except Exception as e:
                        print(f"خطأ في إرسال الرسالة: {e}")
        await asyncio.sleep(300)  # ينتظر 5 دقائق قبل التحديث

# تشغيل البوت
async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(fetch_and_send_news())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())