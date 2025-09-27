import asyncio
import feedparser
import telegram
import sqlite3
import time

# --- الإعدادات ---
# !!! استبدل بالقيم الصحيحة الخاصة بك !!!
TELEGRAM_BOT_TOKEN = '7991360501:AAHeM0qoG_WbNZ3Kpi5jHDjc78i4VWmo7k0'
TELEGRAM_CHANNEL_ID = '@bassam_505'
RSS_FEEDS = [
    'https://www.championat.com/rss/news.xml',
    'https://www.sport-express.ru/rss/news.xml',
    'https://www.sports.ru/rss/main.xml'
]
DB_NAME = 'sent_news.db'
CHECK_INTERVAL_SECONDS = 600  # 600 ثانية = 10 دقائق

# --- إعداد قاعدة البيانات ---
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (link TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# --- التحقق مما إذا كان الرابط قد أُرسل من قبل ---
def is_link_sent(link):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT link FROM news WHERE link=?", (link,))
    result = c.fetchone()
    conn.close()
    return result is not None

# --- إضافة الرابط إلى قاعدة البيانات ---
def add_link_to_db(link):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO news (link) VALUES (?)", (link,))
    conn.commit()
    conn.close()

# --- الوظيفة الرئيسية لجلب الأخبار وإرسالها ---
async def fetch_and_send_news():
    print("بدء دورة تحديث جديدة...")
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            # نعكس القائمة لنبدأ من الأخبار الأقدم إلى الأحدث
            for entry in reversed(feed.entries):
                if not is_link_sent(entry.link):
                    # تنظيف العنوان من الرموز التي قد تسبب مشاكل مع Markdown
                    cleaned_title = entry.title.replace('*', '').replace('_', '').replace('[', '').replace(']', '').replace('`', '')
                    message = f"*{cleaned_title}*\n\n{entry.link}"
                    try:
                        # الطريقة الصحيحة للإرسال في الإصدارات الحديثة
                        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='Markdown')
                        print(f"تم إرسال: {entry.title}")
                        add_link_to_db(entry.link)
                        await asyncio.sleep(1)  # تأخير بسيط بين الرسائل
                    except Exception as e:
                        print(f"!!! فشل في إرسال الخبر: {entry.title}")
                        print(f"!!! سبب الخطأ: {e}")
        except Exception as e:
            print(f"!!! فشل في الوصول إلى الرابط: {feed_url}")
            print(f"!!! سبب الخطأ: {e}")
    print(f"أكملت دورة التحديث، سأنتظر {CHECK_INTERVAL_SECONDS / 60} دقائق.")

# --- وظيفة التشغيل الرئيسية ---
async def main():
    setup_database()
    while True:
        await fetch_and_send_news()
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

# --- نقطة بداية البرنامج ---
if __name__ == '__main__':
    try:
        # لا تنسى استبدال التوكن ومعرف القناة قبل التشغيل
        if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN' or TELEGRAM_CHANNEL_ID == '@your_channel_name':
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! خطأ: يرجى تعديل التوكن ومعرف القناة في ملف bot.py.py")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        print("\nتم إيقاف البوت يدوياً.")