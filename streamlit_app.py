import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import re

st.set_page_config(page_title="Global News Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; font-family: 'Courier New', Courier, monospace; }
    .header { color: #FFFFFF; text-align: center; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 30px; }
    
    /* Category Colors */
    .cat-business { color: #00FFFF; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #00FFFF; padding-left: 10px; background-color: #0d2a2a; padding: 5px 15px;}
    .cat-finance { color: #00FF00; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #00FF00; padding-left: 10px; background-color: #0d2a0d; padding: 5px 15px;}
    .cat-ai { color: #FF00FF; font-size: 22px; font-weight: bold; margin-top: 20px; border-left: 4px solid #FF00FF; padding-left: 10px; background-color: #2a0d2a; padding: 5px 15px;}
    
    /* News Formatting */
    .news-box { border-bottom: 1px dashed #333; padding: 15px 10px; margin-left: 15px; }
    .news-title { color: #E0E0E0; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .news-desc { color: #888888; font-size: 14px; line-height: 1.5; padding-left: 25px; font-style: italic; }
    .bullet { font-weight: bold; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# BBC এবং CNBC-এর রিয়েল-টাইম নিউজ লিংক (যেগুলোতে বিস্তারিত বর্ণনা থাকে)
NEWS_SOURCES = {
    "Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?profile=120000000&id=10000664",
    "AI & Tech": "http://feeds.bbci.co.uk/news/technology/rss.xml"
}

def clean_html(raw_html):
    """বর্ণনার ভেতর কোনো অনাকাঙ্ক্ষিত কোড থাকলে সেটি মুছে পরিষ্কার করবে"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_category_news(url, limit=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item')[:limit]:
            title = item.find('title').text
            
            # খবরের বর্ণনা (Description) ফেচ করা
            desc_element = item.find('description')
            description = desc_element.text if desc_element is not None else "No detailed description available."
            description = clean_html(description)
            
            news_list.append((title, description))
        return news_list
    except:
        return [("⚠️ Failed to connect to news server...", "Retrying in the next cycle...")]

main_placeholder = st.empty()

while True:
    with main_placeholder.container():
        st.markdown("<h1 class='header'>🌐 GLOBAL MARKET & TECH NEWS 🌐</h1>", unsafe_allow_html=True)
        
        # ১. Business Category (Title + Description)
        st.markdown("<div class='cat-business'>🏢 BUSINESS HEADLINES</div>", unsafe_allow_html=True)
        for title, desc in fetch_category_news(NEWS_SOURCES["Business"], 3):
            st.markdown(f"""
                <div class='news-box'>
                    <div class='news-title'><span class='bullet' style='color:#00FFFF;'>➤</span> {title}</div>
                    <div class='news-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # ২. Finance Category (Title + Description)
        st.markdown("<div class='cat-finance'>💰 FINANCE & MARKETS</div>", unsafe_allow_html=True)
        for title, desc in fetch_category_news(NEWS_SOURCES["Finance"], 3):
            st.markdown(f"""
                <div class='news-box'>
                    <div class='news-title'><span class='bullet' style='color:#00FF00;'>➤</span> {title}</div>
                    <div class='news-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # ৩. AI Category (Title + Description)
        st.markdown("<div class='cat-ai'>🤖 ARTIFICIAL INTELLIGENCE & TECH</div>", unsafe_allow_html=True)
        for title, desc in fetch_category_news(NEWS_SOURCES["AI & Tech"], 3):
            st.markdown(f"""
                <div class='news-box'>
                    <div class='news-title'><span class='bullet' style='color:#FF00FF;'>➤</span> {title}</div>
                    <div class='news-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)

    # 60 সেকেন্ডের কাউন্টডাউন
    timer_placeholder = st.empty()
    for remaining in range(60, 0, -1):
        timer_placeholder.markdown(f"<div style='text-align:center; color:#666; margin-top:30px; font-weight:bold;'>🔄 Refreshing live feeds in {remaining:02d} seconds...</div>", unsafe_allow_html=True)
        time.sleep(1)
    timer_placeholder.empty()
    
