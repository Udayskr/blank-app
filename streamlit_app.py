import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Premium Finance News", layout="centered")

# কালার সাইকোলজি ও প্রিমিয়াম ডিজাইন
st.markdown("""
    <style>
    .stApp { background-color: #0A0F1C; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .header { color: #00E5FF; text-align: center; font-size: 28px; font-weight: 900; border-bottom: 3px solid #00E5FF; padding-bottom: 12px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px;}
    
    /* মেইন হেডলাইনের বড় বক্স (Gold Accent) */
    .news-box-new { border-left: 6px solid #FFD700; padding: 25px; margin-bottom: 25px; background-color: #121A2F; border-radius: 0px 10px 10px 0px; box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.5);}
    .news-title-new { color: #FFFFFF; font-size: 30px; font-weight: 800; margin-bottom: 15px; line-height: 1.4;}
    .news-desc-new { color: #E0E0E0; font-size: 20px; line-height: 1.6;}
    
    /* নিচের ৫টি খবরের বক্স (Cyan Accent - No Blur) */
    .news-box-old { border-left: 4px solid #00E5FF; padding: 18px; margin-bottom: 15px; background-color: #121A2F; border-radius: 0px 8px 8px 0px;}
    .news-title-old { color: #FFFFFF; font-size: 20px; font-weight: bold; margin-bottom: 8px;}
    .news-desc-old { color: #B0BEC5; font-size: 16px; line-height: 1.5;}
    </style>
""", unsafe_allow_html=True)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

# অদরকারি বা পার্সোনাল খবর ফিল্টার করার লজিক
def is_hard_finance_news(title):
    lower_title = title.lower()
    # এই শব্দগুলো থাকলে খবরটি স্কিপ করবে
    fluff_keywords = ["how i", "i was", "my ", " me ", "addiction", "shopping", "diary", "opinion", "we tried", "lifestyle"]
    for word in fluff_keywords:
        if word in lower_title:
            return False
    return True

def fetch_finance_news():
    url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item'):
            title = item.find('title').text.strip()
            # পাইথন দিয়ে চেক করা হচ্ছে খবরটি কাজের কিনা
            if not is_hard_finance_news(title):
                continue
                
            desc_element = item.find('description')
            desc = desc_element.text if desc_element is not None else ""
            news_list.append((title, clean_html(desc)))
            
            # অন্তত ১৫টি জেনুইন খবর যোগ করবে
            if len(news_list) == 15:
                break
        return news_list
    except Exception as e:
        return str(e)

main_area = st.empty()

while True:
    news_items = fetch_finance_news()
    
    if not news_items or isinstance(news_items, str):
        with main_area.container():
            st.markdown("<h3 style='color:#FF5252; text-align:center;'>⚠️ Live Feed Interrupted. Reconnecting...</h3>", unsafe_allow_html=True)
            time.sleep(10)
        continue
        
    display_history = []
    
    for index, (title, desc) in enumerate(news_items, 1):
        display_history.insert(0, (title, desc))
        # এখন স্ক্রিনে মোট ৬টি খবর থাকবে (১টি মেইন + ৫টি পুরোনো)
        if len(display_history) > 6:
            display_history.pop()
            
        with main_area.container():
            st.markdown("<div class='header'>📊 GLOBAL MARKET NEWS (LIVE)</div>", unsafe_allow_html=True)
            
            esc_title = title.replace('"', '\\"').replace("'", "\\'")
            esc_desc = desc.replace('"', '\\"').replace("'", "\\'")
            
            # ন্যাচারাল ভয়েস সিলেকশন স্ক্রিপ্ট
            voice_script = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{esc_title}. {esc_desc}");
                    msg.lang = 'en-US';
                    msg.rate = 0.95;
                    msg.pitch = 1.05;
                    
                    var voices = window.speechSynthesis.getVoices();
                    var bestVoice = voices.find(v => v.name.includes('Google UK English Female') || v.name.includes('Female'));
                    if (bestVoice) {{
                        msg.voice = bestVoice;
                    }}
                    window.speechSynthesis.speak(msg);
                }}
            </script>
            """
            components.html(voice_script, width=0, height=0)
            
            top_news_placeholder = st.empty()
            
            old_news_html = ""
            # নিচের ৫টি খবরের ফুল ডিটেইলস
            for old_idx in range(1, len(display_history)):
                old_title, old_desc = display_history[old_idx]
                old_news_html += f"""
                <div class='news-box-old'>
                    <div class='news-title-old'>➤ {old_title}</div>
                    <div class='news-desc-old'>{old_desc}</div> 
                </div>
                """
            st.markdown(old_news_html, unsafe_allow_html=True)
            st.markdown(f"<div style='color:#78909C; text-align:right; font-size:14px; margin-top:25px; font-weight:bold;'>News {index}/{len(news_items)} | Source: Premium Business Feed</div>", unsafe_allow_html=True)
            
            typed_title = ""
            for char in title:
                typed_title += char
                top_news_placeholder.markdown(f"""
                <div class='news-box-new'>
                    <div class='news-title-new'>{typed_title}</div>
                    <div class='news-desc-new'></div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.01) 
                
            time.sleep(0.2) 
            
            typed_desc = ""
            for char in desc:
                typed_desc += char
                top_news_placeholder.markdown(f"""
                <div class='news-box-new'>
                    <div class='news-title-new'>{title}</div>
                    <div class='news-desc-new'>{typed_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.005) 
                
        # বর্ণনা বড় হওয়ায় পড়ার জন্য সময় বাড়িয়ে ২২ সেকেন্ড করা হলো
        time.sleep(22) 
        
    with main_area.container():
        st.markdown("<h3 style='color:#FFD700; text-align:center; padding: 50px 0;'>🔄 Analyzing Next Market Trend...</h3>", unsafe_allow_html=True)
    time.sleep(3)
            
