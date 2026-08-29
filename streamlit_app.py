import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time

st.set_page_config(page_title="Global News Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; font-family: 'Courier New', Courier, monospace; }
    .header { color: #FFFFFF; text-align: center; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 30px; }
    
    /* Category Colors */
    .cat-business { color: #00FFFF; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #00FFFF; padding-left: 10px; background-color: #0d2a2a; padding: 5px 15px;}
    .cat-finance { color: #00FF00; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #00FF00; padding-left: 10px; background-color: #0d2a0d; padding: 5px 15px;}
    .cat-ai { color: #FF00FF; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #FF00FF; padding-left: 10px; background-color: #2a0d2a; padding: 5px 15px;}
    
    .news-card { border-bottom: 1px dashed #333; padding: 12px 10px; margin-left: 15px; color: #E0E0E0; font-size: 16px; }
    .bullet { font-weight: bold; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# ক্যাটাগরি অনুযায়ী গুগলের রিয়েল-টাইম নিউজ লিংক
NEWS_SOURCES = {
    "Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
    "Finance": "https://news.google.com/rss/search?q=Finance+OR+Stock+Market&hl=en-US&gl=US&ceid=US:en",
    "AI & Tech": "https://news.google.com/rss/search?q=Artificial+Intelligence+OR+Technology&hl=en-US&gl=US&ceid=US:en"
}

def fetch_category_news(url, limit=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        root = ET.fromstring(response.content)
        news_list = []
        # নির্দিষ্ট লিমিট (৩টি) পর্যন্ত খবর সংগ্রহ করবে
        for item in root.findall('./channel/item')[:limit]:
            # খবরের টাইটেল থেকে ওয়েবসাইটের নাম (যেমন: - Reuters) মুছে ফেলার লজিক
            title = item.find('title').text.rsplit(' - ', 1)[0]
            news_list.append(title)
        return news_list
    except:
        return ["⚠️ Failed to connect to news server..."]

main_placeholder = st.empty()

while True:
    with main_placeholder.container():
        st.markdown("<h1 class='header'>🌐 GLOBAL MARKET & TECH NEWS 🌐</h1>", unsafe_allow_html=True)
        
        # ১. Business Category
        st.markdown("<div class='cat-business'>🏢 BUSINESS HEADLINES</div>", unsafe_allow_html=True)
        business_news = fetch_category_news(NEWS_SOURCES["Business"], 3)
        for news in business_news:
            st.markdown(f"<div class='news-card'><span class='bullet' style='color:#00FFFF;'>➤</span> {news}</div>", unsafe_allow_html=True)
            
        # ২. Finance Category
        st.markdown("<div class='cat-finance'>💰 FINANCE & MARKETS</div>", unsafe_allow_html=True)
        finance_news = fetch_category_news(NEWS_SOURCES["Finance"], 3)
        for news in finance_news:
            st.markdown(f"<div class='news-card'><span class='bullet' style='color:#00FF00;'>➤</span> {news}</div>", unsafe_allow_html=True)
            
        # ৩. AI Category
        st.markdown("<div class='cat-ai'>🤖 ARTIFICIAL INTELLIGENCE</div>", unsafe_allow_html=True)
        ai_news = fetch_category_news(NEWS_SOURCES["AI & Tech"], 3)
        for news in ai_news:
            st.markdown(f"<div class='news-card'><span class='bullet' style='color:#FF00FF;'>➤</span> {news}</div>", unsafe_allow_html=True)

    # 60 সেকেন্ডের কাউন্টডাউন
    timer_placeholder = st.empty()
    for remaining in range(60, 0, -1):
        timer_placeholder.markdown(f"<div style='text-align:center; color:#666; margin-top:30px; font-weight:bold;'>🔄 Refreshing live feeds in {remaining:02d} seconds...</div>", unsafe_allow_html=True)
        time.sleep(1)
    timer_placeholder.empty()
                
