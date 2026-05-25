import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ====================== НАСТРОЙКИ ======================
st.set_page_config(page_title="SciFlow", layout="wide", page_icon="🧪")

TELEGRAM_TOKEN = "8177168221:AAHT1oULEWi7_0-Wt9vMGQJVInZNEZq7PDA"
TELEGRAM_CHAT_ID = "133660500"
PASSWORD = "1"

MSK = timezone(timedelta(hours=3))

SOURCES = {
    # ================= EN: Academic & Research =================
    "Nature News": {"url": "https://www.nature.com/nature.rss", "lang": "en"},
    "Nature Communications": {"url": "https://feeds.nature.com/ncomms/rss/current", "lang": "en"},
    "Nature Climate Change": {"url": "https://feeds.nature.com/nclimate/rss/current", "lang": "en"},
    "Nature Genetics": {"url": "https://feeds.nature.com/ng/rss/current", "lang": "en"},
    "Nature Neuroscience": {"url": "https://feeds.nature.com/neuro/rss/current", "lang": "en"},
    "Nature Physics": {"url": "https://feeds.nature.com/nphys/rss/current", "lang": "en"},
    "Science.org": {"url": "https://www.science.org/rss/news_current.xml", "lang": "en"},
    "PNAS": {"url": "https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=PNAS", "lang": "en"},
    "arXiv": {"url": "https://export.arxiv.org/rss/physics", "lang": "en"},
    
    # ================= EN: News & Aggregators =================
    "Science News": {"url": "https://www.sciencenews.org/feed", "lang": "en"},
    "ScienceDaily": {"url": "https://www.sciencedaily.com/rss/all.xml", "lang": "en"},
    "EurekAlert": {"url": "https://www.eurekalert.org/rss.xml", "lang": "en"},
    "Futurity": {"url": "https://www.futurity.org/feed/", "lang": "en"},
    "Phys.org": {"url": "https://phys.org/rss-feed/", "lang": "en"},
    "Medical Xpress": {"url": "https://medicalxpress.com/rss-feed/", "lang": "en"},
    "TechXplore": {"url": "https://techxplore.com/rss-feed/", "lang": "en"},
    "Neuroscience News": {"url": "https://neurosciencenews.com/feed/", "lang": "en"},
    "Strategian Universe": {"url": "https://sciencenews.strategian.com/public_html/feed/", "lang": "en"},
    
    # ================= EN: Major Media (Science) =================
    "BBC Science": {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "lang": "en"},
    "NYT Science": {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "lang": "en"},
    "The Guardian Science": {"url": "https://www.theguardian.com/science/rss", "lang": "en"},
    "Daily Mail Science": {"url": "https://www.dailymail.co.uk/sciencetech/article-14373739/rss", "lang": "en"},
    "Space.com": {"url": "https://www.space.com/feeds/all", "lang": "en"},
    "ScienceAlert": {"url": "https://www.sciencealert.com/feed", "lang": "en"},
    
    # ================= EN: Tech & Deep Science =================
    "Ars Technica Science": {"url": "https://feeds.arstechnica.com/arstechnica/science", "lang": "en"},
    "Wired Science": {"url": "https://www.wired.com/feed/category/science/latest/rss", "lang": "en"},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/feed/", "lang": "en"},
    "Quanta Magazine": {"url": "https://www.quantamagazine.org/feed/", "lang": "en"},
    "The Conversation": {"url": "https://theconversation.com/science/articles.atom", "lang": "en"},
    
    # ================= EN: Universities =================
    "MIT News": {"url": "https://news.mit.edu/rss/feed", "lang": "en"},
    "Stanford News": {"url": "https://news.stanford.edu/feed/", "lang": "en"},
    "Harvard Gazette": {"url": "https://news.harvard.edu/gazette/feed/", "lang": "en"},
    "Caltech News": {"url": "https://www.caltech.edu/about/news/feed", "lang": "en"},
    "Oxford Science": {"url": "https://www.ox.ac.uk/feeds/rss/science", "lang": "en"},
    "Cambridge Research": {"url": "https://www.cam.ac.uk/research/feed", "lang": "en"},
    "Max Planck Society": {"url": "https://www.mpg.de/rss-feeds/news", "lang": "en"},
    "ETH Zurich": {"url": "https://ethz.ch/en/news-and-events/eth-news.rss", "lang": "en"},
    "CNRS News": {"url": "https://www.cnrs.fr/en/rss/feed", "lang": "en"},
    
    # ================= EN: Agencies & Orgs =================
    "CERN News": {"url": "https://home.cern/rss/news", "lang": "en"},
    "NASA Breaking News": {"url": "https://www.nasa.gov/news-release/feed/", "lang": "en"},
    "ESA Space Science": {"url": "https://www.esa.int/rssfeed/Our_Activities/Space_Science", "lang": "en"},
    "WHO News": {"url": "https://www.who.int/rss-feeds/news-english.xml", "lang": "en"},
    "CDC News": {"url": "https://tools.cdc.gov/api/v2/resources/media/news.rss", "lang": "en"},
    
    # ================= RU: News & Aggregators =================
    "N+1": {"url": "https://nplus1.ru/rss", "lang": "ru"},
    "Naked Science": {"url": "https://naked-science.ru/feed", "lang": "ru"},
    "Коммерсант Наука": {"url": "https://www.kommersant.ru/RSS/section-science.xml", "lang": "ru"},
    "РБК Life Наука": {"url": "https://www.rbc.ru/life/tag/science/rss/", "lang": "ru"},
    "Lenta.ru Наука": {"url": "https://lenta.ru/rss/news/science", "lang": "ru"},
    
    # ================= RU: Universities =================
    "Skoltech News": {"url": "https://www.skoltech.ru/feed/", "lang": "ru"},
    "MIPT News": {"url": "https://mipt.ru/feed/", "lang": "ru"},
    "HSE Science": {"url": "https://www.hse.ru/rss/science", "lang": "ru"},
}

# ====================== АВТОРИЗАЦИЯ ======================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🧬 SciFlow — Мониторинг научпопа")
    pw = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Неверный пароль")
    st.stop()

# ====================== ФУНКЦИИ ======================
def send_telegram(text: str):
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
    except:
        pass

def load_news():
    all_items = []
    
    for name, info in SOURCES.items():
        try:
            feed = feedparser.parse(info["url"])
            for entry in feed.entries[:8]:
                all_items.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "source": name,
                    "lang": info["lang"]
                })
        except:
            continue

    if all_items:
        send_telegram(f"🧪 SciFlow\nСобрано новостей: {len(all_items)}")

    en = defaultdict(list)
    ru = defaultdict(list)
    for item in all_items:
        if item["lang"] == "ru":
            ru[item["source"]].append(item)
        else:
            en[item["source"]].append(item)

    return {
        "en": dict(en),
        "ru": dict(ru),
        "total": len(all_items),
        "timestamp": datetime.now(MSK).strftime("%d %b %Y, %H:%M MSK")
    }

# ====================== ИНТЕРФЕЙС ======================
st.title("🧬 SciFlow — Мониторинг научпопа")
st.caption("Простая облачная версия")

if st.button("🔄 Обновить новости", type="primary"):
    with st.spinner("Загружаю новости..."):
        data = load_news()
    st.success(f"Обновлено • {data['timestamp']} • Новостей: {data['total']}")
    st.rerun()

data = load_news()

tab1, tab2 = st.tabs(["🌍 Global Science", "🇷🇺 Российский научпоп"])

with tab1:
    for source, items in data["en"].items():
        with st.expander(f"**{source}** — {len(items)} новостей"):
            for item in items:
                st.markdown(f"[{item['title']}]({item['link']})")

with tab2:
    for source, items in data["ru"].items():
        with st.expander(f"**{source}** — {len(items)} новостей"):
            for item in items:
                st.markdown(f"[{item['title']}]({item['link']})")

st.caption("SciFlow • Однофайловая версия")
