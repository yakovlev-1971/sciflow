import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ====================== НАСТРОЙКИ ======================
st.set_page_config(page_title="SciFlow", layout="wide", page_icon="🧪")

TELEGRAM_TOKEN = "8177168221:AAHT1oULEWi7_0-Wt9vMGQJVInZNEZq7PDA"
TELEGRAM_CHAT_ID = "133660500"
PASSWORD = "наука2026"          # ← Обязательно поменяй!

MSK = timezone(timedelta(hours=3))

SOURCES = {
    "Nature": {"url": "https://www.nature.com/nature.rss", "lang": "en"},
    "Science.org": {"url": "https://www.science.org/rss/news_current.xml", "lang": "en"},
    "N+1": {"url": "https://nplus1.ru/rss", "lang": "ru"},
    "Naked Science": {"url": "https://naked-science.ru/feed", "lang": "ru"},
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

    # Отправляем уведомление в Telegram
    if all_items:
        send_telegram(f"🧪 SciFlow\nСобрано новостей: {len(all_items)}")

    # Группировка
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

# Загружаем данные
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
