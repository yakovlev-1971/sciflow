import streamlit as st
import feedparser
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ====================== НАСТРОЙКИ ======================
st.set_page_config(page_title="SciFlow", layout="wide", page_icon="🧪")

PASSWORD = "1"
MSK = timezone(timedelta(hours=3))
AUTO_UPDATE_INTERVAL = 600

SOURCES = {
    # ================= EN: Academic & Research =================
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

# ====================== АВТОРИЗАЦИЯ ======================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🧬 SciFlow — Последние новости науки")
    pw = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Неверный пароль")
    st.stop()

# ====================== ФУНКЦИИ ======================

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
                    "source": name,
                    "lang": info["lang"]
                })
        except:
            continue

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


# ====================== АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ======================
if "last_update" not in st.session_state:
    st.session_state.last_update = 0

if time.time() - st.session_state.last_update > AUTO_UPDATE_INTERVAL:
    data = load_news()
    st.session_state.news_data = data
    st.session_state.last_update = time.time()
else:
    data = st.session_state.get("news_data", load_news())

# ====================== ИНТЕРФЕЙС ======================
st.title("🧬 SciFlow — Последние новости науки")
st.caption("Простая облачная версия")

if st.button("🔄 Обновить", type="primary"):
    with st.spinner("Загружаю новости..."):
        data = load_news()
    st.success(f"Обновлено • {data['timestamp']} • Новостей: {data['total']}")
    st.rerun()

data = load_news()

tab1, tab2 = st.tabs(["🌍 Global Science", "🇷🇺 Russian Science"])

with tab1:
    for source, items in data["en"].items():
        with st.expander(f"**{source}**"):
            for item in items:
                st.markdown(f"[{item['title']}]({item['link']})")

with tab2:
    for source, items in data["ru"].items():
        with st.expander(f"**{source}**"):
            for item in items:
                st.markdown(f"[{item['title']}]({item['link']})")

st.caption("SciFlow • © Denis Yakovlev, 2026")
