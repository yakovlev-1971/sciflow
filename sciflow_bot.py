import feedparser
import requests
import json
import os
import time
from datetime import datetime, timezone, timedelta

# ====================== НАСТРОЙКИ ======================
TELEGRAM_TOKEN = "8177168221:AAHT1oULEWi7_0-Wt9vMGQJVInZNEZq7PDA"
TELEGRAM_CHAT_ID = "133660500"
MSK = timezone(timedelta(hours=3))
CHECK_INTERVAL = 900  # 15 минут

CACHE_FILE = os.path.expanduser("~/sciflow_cache.json")

SOURCES = {
    "Nature News": {"url": "https://www.nature.com/nature.rss", "lang": "en", "enabled": True},
    "Nature Communications": {"url": "https://feeds.nature.com/ncomms/rss/current", "lang": "en", "enabled": False},
    "Nature Climate Change": {"url": "https://feeds.nature.com/nclimate/rss/current", "lang": "en", "enabled": False},
    "Nature Genetics": {"url": "https://feeds.nature.com/ng/rss/current", "lang": "en", "enabled": False},
    "Nature Neuroscience": {"url": "https://feeds.nature.com/neuro/rss/current", "lang": "en", "enabled": False},
    "Nature Physics": {"url": "https://feeds.nature.com/nphys/rss/current", "lang": "en", "enabled": False},
    "Science.org": {"url": "https://www.science.org/rss/news_current.xml", "lang": "en", "enabled": True},
    "PNAS": {"url": "https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=PNAS", "lang": "en", "enabled": True},
    "arXiv": {"url": "https://export.arxiv.org/rss/physics", "lang": "en", "enabled": True},
    "Science News": {"url": "https://www.sciencenews.org/feed", "lang": "en", "enabled": True},
    "ScienceDaily": {"url": "https://www.sciencedaily.com/rss/all.xml", "lang": "en", "enabled": True},
    "EurekAlert": {"url": "https://www.eurekalert.org/rss.xml", "lang": "en", "enabled": True},
    "Futurity": {"url": "https://www.futurity.org/feed/", "lang": "en", "enabled": True},
    "Phys.org": {"url": "https://phys.org/rss-feed/", "lang": "en", "enabled": True},
    "Medical Xpress": {"url": "https://medicalxpress.com/rss-feed/", "lang": "en", "enabled": True},
    "TechXplore": {"url": "https://techxplore.com/rss-feed/", "lang": "en", "enabled": True},
    "Neuroscience News": {"url": "https://neurosciencenews.com/feed/", "lang": "en", "enabled": True},
    "Strategian Universe": {"url": "https://sciencenews.strategian.com/public_html/feed/", "lang": "en", "enabled": True},
    "BBC Science": {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "lang": "en", "enabled": True},
    "NYT Science": {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "lang": "en", "enabled": True},
    "The Guardian Science": {"url": "https://www.theguardian.com/science/rss", "lang": "en", "enabled": True},
    "Daily Mail Science": {"url": "https://www.dailymail.co.uk/sciencetech/article-14373739/rss", "lang": "en", "enabled": True},
    "Space.com": {"url": "https://www.space.com/feeds/all", "lang": "en", "enabled": True},
    "ScienceAlert": {"url": "https://www.sciencealert.com/feed", "lang": "en", "enabled": True},
    "Ars Technica Science": {"url": "https://feeds.arstechnica.com/arstechnica/science", "lang": "en", "enabled": True},
    "Wired Science": {"url": "https://www.wired.com/feed/category/science/latest/rss", "lang": "en", "enabled": True},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/feed/", "lang": "en", "enabled": True},
    "Quanta Magazine": {"url": "https://www.quantamagazine.org/feed/", "lang": "en", "enabled": True},
    "The Conversation": {"url": "https://theconversation.com/science/articles.atom", "lang": "en", "enabled": True},
    "MIT News": {"url": "https://news.mit.edu/rss/feed", "lang": "en", "enabled": True},
    "Stanford News": {"url": "https://news.stanford.edu/feed/", "lang": "en", "enabled": True},
    "Harvard Gazette": {"url": "https://news.harvard.edu/gazette/feed/", "lang": "en", "enabled": True},
    "Caltech News": {"url": "https://www.caltech.edu/about/news/feed", "lang": "en", "enabled": True},
    "Oxford Science": {"url": "https://www.ox.ac.uk/feeds/rss/science", "lang": "en", "enabled": True},
    "Cambridge Research": {"url": "https://www.cam.ac.uk/research/feed", "lang": "en", "enabled": True},
    "Max Planck Society": {"url": "https://www.mpg.de/rss-feeds/news", "lang": "en", "enabled": True},
    "ETH Zurich": {"url": "https://ethz.ch/en/news-and-events/eth-news.rss", "lang": "en", "enabled": True},
    "CNRS News": {"url": "https://www.cnrs.fr/en/rss/feed", "lang": "en", "enabled": True},
    "CERN News": {"url": "https://home.cern/rss/news", "lang": "en", "enabled": True},
    "NASA Breaking News": {"url": "https://www.nasa.gov/news-release/feed/", "lang": "en", "enabled": True},
    "ESA Space Science": {"url": "https://www.esa.int/rssfeed/Our_Activities/Space_Science", "lang": "en", "enabled": True},
    "WHO News": {"url": "https://www.who.int/rss-feeds/news-english.xml", "lang": "en", "enabled": True},
    "CDC News": {"url": "https://tools.cdc.gov/api/v2/resources/media/news.rss", "lang": "en", "enabled": True},
    "N+1": {"url": "https://nplus1.ru/rss", "lang": "ru", "enabled": True},
    "Naked Science": {"url": "https://naked-science.ru/feed", "lang": "ru", "enabled": True},
    "Коммерсант Наука": {"url": "https://www.kommersant.ru/RSS/section-science.xml", "lang": "ru", "enabled": False},
    "РБК Life Наука": {"url": "https://www.rbc.ru/life/tag/science/rss/", "lang": "ru", "enabled": False},
    "Lenta.ru Наука": {"url": "https://lenta.ru/rss/news/science", "lang": "ru", "enabled": False},
    "Skoltech News": {"url": "https://www.skoltech.ru/feed/", "lang": "ru", "enabled": False},
    "MIPT News": {"url": "https://mipt.ru/feed/", "lang": "ru", "enabled": False},
    "HSE Science": {"url": "https://www.hse.ru/rss/science", "lang": "ru", "enabled": False},
}

# ====================== ФУНКЦИИ ======================

def send_telegram(text: str):
    """Отправляет сообщение в Telegram."""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


def load_previous_titles():
    """Загружает список предыдущих заголовков из кэша."""
    try:
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_current_titles(titles):
    """Сохраняет текущие заголовки в кэш."""
    with open(CACHE_FILE, "w") as f:
        json.dump(list(titles), f)


def load_news():
    """Собирает все новости из RSS-источников."""
    all_items = []
    
    for name, info in SOURCES.items():
        if not info.get("enabled", True):
            continue
        
        try:
            feed = feedparser.parse(info["url"])
            for entry in feed.entries[:5]:
                all_items.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "source": name
                })
        except:
            continue

    return all_items


def check_and_notify():
    """Проверяет новости и отправляет уведомления о новых."""
    print(f"[{datetime.now(MSK).strftime('%H:%M')}] Проверяю новости...")
    
    all_items = load_news()
    current_titles = set(item["title"] for item in all_items)
    previous_titles = load_previous_titles()
    
    if not previous_titles:
        save_current_titles(current_titles)
        print(f"  Первый запуск. Сохранено {len(current_titles)} заголовков.")
        return
    
    new_titles = current_titles - previous_titles
    
    if new_titles:
        new_items = [item for item in all_items if item["title"] in new_titles]
        titles_text = "\n".join([f"• {item['title']}" for item in new_items[:10]])
        message = f"🧪 SciFlow Update\nСвежих новостей: {len(new_items)}\n\n{titles_text}"
        if len(new_items) > 10:
            message += f"\n\n... и ещё {len(new_items) - 10}"
        send_telegram(message)
        print(f"  Отправлено {len(new_items)} новых новостей.")
    else:
        print("  Новых новостей нет.")
    
    save_current_titles(current_titles)


# ====================== ГЛАВНЫЙ ЦИКЛ ======================

if __name__ == "__main__":
    print("🚀 SciFlow Bot запущен.")
    send_telegram("🧪 SciFlow Bot запущен. Буду присылать свежие новости каждые 15 минут.")
    
    while True:
        try:
            check_and_notify()
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")
            send_telegram(f"⚠️ SciFlow: ошибка при проверке новостей.\n{e}")
        
        time.sleep(CHECK_INTERVAL)
