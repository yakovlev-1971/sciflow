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
    "Nature News": {"url": "https://www.nature.com/nature.rss", "lang": "en"},
    "Nature Communications": {"url": "https://feeds.nature.com/ncomms/rss/current", "lang": "en"},
    "Nature Climate Change": {"url": "https://feeds.nature.com/nclimate/rss/current", "lang": "en"},
    "Nature Genetics": {"url": "https://feeds.nature.com/ng/rss/current", "lang": "en"},
    "Nature Neuroscience": {"url": "https://feeds.nature.com/neuro/rss/current", "lang": "en"},
    "Nature Physics": {"url": "https://feeds.nature.com/nphys/rss/current", "lang": "en"},
    "Science.org": {"url": "https://www.science.org/rss/news_current.xml", "lang": "en"},
    "PNAS": {"url": "https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=PNAS", "lang": "en"},
    "arXiv": {"url": "https://export.arxiv.org/rss/physics", "lang": "en"},
    "Science News": {"url": "https://www.sciencenews.org/feed", "lang": "en"},
    "ScienceDaily": {"url": "https://www.sciencedaily.com/rss/all.xml", "lang": "en"},
    "EurekAlert": {"url": "https://www.eurekalert.org/rss.xml", "lang": "en"},
    "Futurity": {"url": "https://www.futurity.org/feed/", "lang": "en"},
    "Phys.org": {"url": "https://phys.org/rss-feed/", "lang": "en"},
    "Medical Xpress": {"url": "https://medicalxpress.com/rss-feed/", "lang": "en"},
    "TechXplore": {"url": "https://techxplore.com/rss-feed/", "lang": "en"},
    "Neuroscience News": {"url": "https://neurosciencenews.com/feed/", "lang": "en"},
    "Strategian Universe": {"url": "https://sciencenews.strategian.com/public_html/feed/", "lang": "en"},
    "BBC Science": {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "lang": "en"},
    "NYT Science": {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "lang": "en"},
    "The Guardian Science": {"url": "https://www.theguardian.com/science/rss", "lang": "en"},
    "Daily Mail Science": {"url": "https://www.dailymail.co.uk/sciencetech/article-14373739/rss", "lang": "en"},
    "Space.com": {"url": "https://www.space.com/feeds/all", "lang": "en"},
    "ScienceAlert": {"url": "https://www.sciencealert.com/feed", "lang": "en"},
    "Ars Technica Science": {"url": "https://feeds.arstechnica.com/arstechnica/science", "lang": "en"},
    "Wired Science": {"url": "https://www.wired.com/feed/category/science/latest/rss", "lang": "en"},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/feed/", "lang": "en"},
    "Quanta Magazine": {"url": "https://www.quantamagazine.org/feed/", "lang": "en"},
    "The Conversation": {"url": "https://theconversation.com/science/articles.atom", "lang": "en"},
    "MIT News": {"url": "https://news.mit.edu/rss/feed", "lang": "en"},
    "Stanford News": {"url": "https://news.stanford.edu/feed/", "lang": "en"},
    "Harvard Gazette": {"url": "https://news.harvard.edu/gazette/feed/", "lang": "en"},
    "Caltech News": {"url": "https://www.caltech.edu/about/news/feed", "lang": "en"},
    "Oxford Science": {"url": "https://www.ox.ac.uk/feeds/rss/science", "lang": "en"},
    "Cambridge Research": {"url": "https://www.cam.ac.uk/research/feed", "lang": "en"},
    "Max Planck Society": {"url": "https://www.mpg.de/rss-feeds/news", "lang": "en"},
    "ETH Zurich": {"url": "https://ethz.ch/en/news-and-events/eth-news.rss", "lang": "en"},
    "CNRS News": {"url": "https://www.cnrs.fr/en/rss/feed", "lang": "en"},
    "CERN News": {"url": "https://home.cern/rss/news", "lang": "en"},
    "NASA Breaking News": {"url": "https://www.nasa.gov/news-release/feed/", "lang": "en"},
    "ESA Space Science": {"url": "https://www.esa.int/rssfeed/Our_Activities/Space_Science", "lang": "en"},
    "WHO News": {"url": "https://www.who.int/rss-feeds/news-english.xml", "lang": "en"},
    "CDC News": {"url": "https://tools.cdc.gov/api/v2/resources/media/news.rss", "lang": "en"},
    "N+1": {"url": "https://nplus1.ru/rss", "lang": "ru"},
    "Naked Science": {"url": "https://naked-science.ru/feed", "lang": "ru"},
    "Коммерсант Наука": {"url": "https://www.kommersant.ru/RSS/section-science.xml", "lang": "ru"},
    "РБК Life Наука": {"url": "https://www.rbc.ru/life/tag/science/rss/", "lang": "ru"},
    "Lenta.ru Наука": {"url": "https://lenta.ru/rss/news/science", "lang": "ru"},
    "Skoltech News": {"url": "https://www.skoltech.ru/feed/", "lang": "ru"},
    "MIPT News": {"url": "https://mipt.ru/feed/", "lang": "ru"},
    "HSE Science": {"url": "https://www.hse.ru/rss/science", "lang": "ru"},
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
