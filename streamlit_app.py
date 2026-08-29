import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import re
import streamlit.components.v1 as components

# পেজ সেটআপ
st.set_page_config(page_title="Live Finance News", layout="centered")

# কাস্টম ডিজাইন
st.markdown("""
    <style>
    .stApp { background-color: #050505; font-family: 'Courier New', Courier, monospace; }
    .header { color: #00FF00; text-align: center; font-size: 24px; font-weight: bold; border-bottom: 2px solid #00FF00; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase;}
    .news-box-new { border-left: 5px solid #00FFFF; padding: 15px; margin-bottom: 15px; background-color: #0d1a1a; border-radius: 0px 8px 8px 0px; box-shadow: 0px 0px 10px #00FFFF33;}
    .news-title-new { color: #FFFFFF; font-size: 20px; font-weight: bold; margin-bottom: 8px; line-height: 1.3;}
    .news-desc-new { color: #00FFFF; font-size: 16px; line-height: 1.5; font-style: italic;}
    .news-box-old { border-left: 4px solid #335533; padding: 12px; margin-bottom: 10px; background-color: #050a05; border-radius: 0px 8px 8px 0px; opacity: 0.6;}
    .news-title-old { color: #AAAAAA; font-size: 16px; font-weight: bold; margin-bottom: 5px;}
    .news-desc-old { color: #666666; font-size: 14px; line-height: 1.4; font-style: italic;}
    </style>
""", unsafe_allow_html=True)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

# খবর আনার ফাংশন (BBC Business)
def fetch_finance_news():
    url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item')[:10]: 
            title = item.find('title').text
            desc_element = item.find('description')
            desc = desc_element.text if desc_element is not None else ""
            news_list.append((title.strip(), clean_html(desc)))
        return news_list
    except Exception as e:
        return str(e)

main_area = st.empty()

while True:
    news_items = fetch_finance_news()
    
    if not news_items or isinstance(news_items, str):
        with main_area.container():
            st.markdown("<h3 style='color:red; text-align:center;'>⚠️ Connection Failed. Retrying...</h3>", unsafe_allow_html=True)
            time.sleep(10)
        continue
        
    display_history = []
    
    for index, (title, desc) in enumerate(news_items, 1):
        display_history.insert(0, (title, desc))
        if len(display_history) > 3:
            display_history.pop()
            
        with main_area.container():
            st.markdown("<div class='header'>📈 Finance News (LIVE)</div>", unsafe_allow_html=True)
            
            # --- অটো ভয়েস রিডার (Streamlit Components) ---
            esc_title = title.replace('"', '\\"').replace("'", "\\'")
            esc_desc = desc.replace('"', '\\"').replace("'", "\\'")
            
            voice_script = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{esc_title}... {esc_desc}");
                    msg.lang = 'en-US';
                    msg.rate = 0.9;
                    window.speechSynthesis.speak(msg);
                }}
            </script>
            """
            components.html(voice_script, width=0, height=0)
            
            # নতুন খবরের টাইপরাইটার অ্যানিমেশনের জন্য জায়গা
            top_news_placeholder = st.empty()
            
            # পুরোনো খবরগুলো সাজানো
            old_news_html = ""
            for old_idx in range(1, len(display_history)):
                old_title, old_desc = display_history[old_idx]
                old_news_html += f"""
                <div class='news-box-old'>
                    <div class='news-title-old'>➤ {old_title}</div>
                    <div class='news-desc-old'>{old_desc[:100]}...</div> 
                </div>
                """
            st.markdown(old_news_html, unsafe_allow_html=True)
            st.markdown(f"<div style='color:#444; text-align:right; font-size:12px; margin-top:20px;'>News {index}/10 | Source: BBC Business</div>", unsafe_allow_html=True)
            
            # --- Python দিয়ে টাইপরাইটার অ্যানিমেশন (কখনো ব্লক হবে না) ---
            typed_title = ""
            for char in title:
                typed_title += char
                top_news_placeholder.markdown(f"""
                <div class='news-box-new'>
                    <div class='news-title-new'>{typed_title}</div>
                    <div class='news-desc-new'></div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.02) # টাইটেল লেখার স্পিড
                
            time.sleep(0.3) 
            
            typed_desc = ""
            for char in desc:
                typed_desc += char
                top_news_placeholder.markdown(f"""
                <div class='news-box-new'>
                    <div class='news-title-new'>{title}</div>
                    <div class='news-desc-new'>{typed_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.01) # ডেসক্রিপশন লেখার স্পিড
                
        # পরের খবর আসার আগে ১৫ সেকেন্ড অপেক্ষা করবে
        time.sleep(15) 
        
    with main_area.container():
        st.markdown("<h3 style='color:#00FF00; text-align:center; padding: 50px 0;'>🔄 Syncing New Headlines...</h3>", unsafe_allow_html=True)
    time.sleep(3)
            
