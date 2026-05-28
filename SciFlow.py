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
