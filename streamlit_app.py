import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import re
import json

st.set_page_config(page_title="Global Market News", layout="centered")

# প্রিমিয়াম ডিজাইন ও স্মুথ অ্যানিমেশন সিএসএস
st.markdown("""
    <style>
    .stApp { background-color: #0A0F1C; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .header { color: #00E5FF; text-align: center; font-size: 28px; font-weight: 900; border-bottom: 3px solid #00E5FF; padding-bottom: 12px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px;}
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .news-box-new { 
        border-left: 6px solid #FFD700; 
        padding: 25px; 
        margin-bottom: 25px; 
        background-color: #121A2F; 
        border-radius: 0px 10px 10px 0px; 
        box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.5);
        animation: slideIn 0.6s ease-out;
    }
    .news-title-new { color: #FFFFFF; font-size: 28px; font-weight: 800; margin-bottom: 15px; line-height: 1.4;}
    .news-desc-new { color: #E0E0E0; font-size: 18px; line-height: 1.6;}
    
    .news-box-old { border-left: 4px solid #00E5FF; padding: 18px; margin-bottom: 15px; background-color: #121A2F; border-radius: 0px 8px 8px 0px;}
    .news-title-old { color: #FFFFFF; font-size: 20px; font-weight: bold; margin-bottom: 8px;}
    .news-desc-old { color: #B0BEC5; font-size: 16px; line-height: 1.5;}
    </style>
""", unsafe_allow_html=True)

def clean_text(text):
    clean = re.sub(r'<.*?>', '', text)
    clean = re.sub(r'BBC Homepage.*?(?=\w)', '', clean, flags=re.IGNORECASE)
    return clean.strip()

def get_full_article_details(url, backup_desc):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', res.text, re.DOTALL)
        clean_paras = []
        for p in paragraphs:
            clean_p = clean_text(p)
            if len(clean_p.split()) > 8 and "Copyright" not in clean_p and "Getty" not in clean_p:
                clean_paras.append(clean_p)
        
        if clean_paras:
            combined = " ".join(clean_paras[:2])
            return combined
        return clean_text(backup_desc)
    except:
        return clean_text(backup_desc)

def fetch_finance_news():
    url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item')[:15]:
            title = clean_text(item.find('title').text)
            link = item.find('link').text.strip()
            
            if any(word in title.lower() for word in ["how i", "i was", "my ", " me ", "addiction"]):
                continue
                
            desc_element = item.find('description')
            backup_desc = desc_element.text if desc_element is not None else ""
            
            full_desc = get_full_article_details(link, backup_desc)
            news_list.append((title, full_desc))
            
            if len(news_list) >= 10:
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
        if len(display_history) > 6:
            display_history.pop()
            
        with main_area.container():
            st.markdown("<div class='header'>📊 GLOBAL MARKET NEWS (LIVE)</div>", unsafe_allow_html=True)
            
            js_title = json.dumps(title)
            js_desc = json.dumps(desc)
            
            # নিখুঁত ভয়েস এবং স্টাইলিশ এন্ট্রি বক্স
            live_html = f"""
            <div class='news-box-new'>
                <div class='news-title-new'>{title}</div>
                <div class='news-desc-new'>{desc}</div>
            </div>
            
            <script>
            (function() {{
                const titleText = {js_title};
                const descText = {js_desc};
                
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(titleText + ". " + descText);
                    utterance.lang = 'en-US';
                    utterance.rate = 0.95;
                    
                    const voices = window.speechSynthesis.getVoices();
                    const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Female'));
                    if (preferredVoice) {{
                        utterance.voice = preferredVoice;
                    }}
                    window.speechSynthesis.speak(utterance);
                }}
            }})();
            </script>
            """
            st.markdown(live_html, unsafe_allow_html=True)
            
            # নিচের পুরোনো খবরগুলো
            old_news_html = ""
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
            
        time.sleep(25) 
        
    with main_area.container():
        st.markdown("<h3 style='color:#FFD700; text-align:center; padding: 50px 0;'>🔄 Analyzing Next Market Trend...</h3>", unsafe_allow_html=True)
    time.sleep(3)
    
