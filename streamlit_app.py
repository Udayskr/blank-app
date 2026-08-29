import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import re
from gtts import gTTS
import base64
from io import BytesIO

st.set_page_config(page_title="Live Finance News", layout="centered")

# --- কাস্টম সিএসএস (মোবাইল ও পিসি উভয়ের জন্য পারফেক্ট) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; font-family: 'Courier New', Courier, monospace; }
    .header { color: #00FF00; text-align: center; font-size: 24px; font-weight: bold; border-bottom: 2px solid #00FF00; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase;}
    
    /* নতুন খবরের ডিজাইন */
    .news-box-new { border-left: 5px solid #00FFFF; padding: 15px; margin-bottom: 15px; background-color: #0d1a1a; border-radius: 0px 8px 8px 0px; box-shadow: 0px 0px 10px #00FFFF33;}
    .news-title-new { color: #FFFFFF; font-size: 20px; font-weight: bold; margin-bottom: 8px; line-height: 1.3;}
    .news-desc-new { color: #00FFFF; font-size: 16px; line-height: 1.5; font-style: italic;}
    
    /* পুরোনো খবরের ডিজাইন (হালকা ঝাপসা) */
    .news-box-old { border-left: 4px solid #335533; padding: 12px; margin-bottom: 10px; background-color: #050a05; border-radius: 0px 8px 8px 0px; opacity: 0.6;}
    .news-title-old { color: #AAAAAA; font-size: 16px; font-weight: bold; margin-bottom: 5px;}
    .news-desc-old { color: #666666; font-size: 14px; line-height: 1.4; font-style: italic;}
    </style>
""", unsafe_allow_html=True)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_finance_news():
    url = "https://search.cnbc.com/rs/search/combinedcms/view.xml?profile=120000000&id=10000664"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        root = ET.fromstring(response.content)
        news_list = []
        for item in root.findall('./channel/item')[:10]: 
            title = item.find('title').text
            desc_element = item.find('description')
            desc = desc_element.text if desc_element is not None else ""
            news_list.append((title.strip(), clean_html(desc)))
        return news_list
    except:
        return []

def get_audio_html(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except:
        return ""

main_area = st.empty()

while True:
    news_items = fetch_finance_news()
    
    if not news_items:
        with main_area.container():
            st.markdown("<h3 style='color:red; text-align:center;'>⚠️ Network Error. Retrying...</h3>", unsafe_allow_html=True)
        time.sleep(10)
        continue
        
    display_history = [] # এখানে সর্বোচ্চ ৩টি খবর জমা থাকবে
    
    for index, (title, desc) in enumerate(news_items, 1):
        # নতুন খবরটি তালিকার একদম ওপরে যুক্ত করা হচ্ছে
        display_history.insert(0, (title, desc))
        
        # ৩টির বেশি খবর হয়ে গেলে শেষেরটি মুছে ফেলবে
        if len(display_history) > 3:
            display_history.pop()
            
        # ভয়েস অডিও জেনারেট
        audio_html = get_audio_html(f"{title}. {desc}")
        
        with main_area.container():
            st.markdown("<div class='header'>📈 Finance News (LIVE)</div>", unsafe_allow_html=True)
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # --- ১. নতুন খবরের টাইপরাইটার ইফেক্ট ---
            new_title, new_desc = display_history[0]
            # জাভাস্ক্রিপ্ট এরর এড়াতে ক্যারেক্টার এস্কেপ করা
            esc_title = new_title.replace('"', '\\"').replace("'", "\\'")
            esc_desc = new_desc.replace('"', '\\"').replace("'", "\\'")
            
            html_content = f"""
            <div class='news-box-new'>
                <div class='news-title-new' id='title-{index}'></div>
                <div class='news-desc-new' id='desc-{index}'></div>
            </div>
            
            <script>
            (function() {{
                const titleStr = "{esc_title}";
                const descStr = "{esc_desc}";
                let ti = 0; let di = 0;
                const speed = 40; // টাইপিং স্পিড
                
                function typeTitle() {{
                    if (ti < titleStr.length) {{
                        document.getElementById('title-{index}').innerHTML += titleStr.charAt(ti);
                        ti++;
                        setTimeout(typeTitle, speed);
                    }} else {{
                        setTimeout(typeDesc, 200); // টাইটেল শেষ হলে একটু থেমে বর্ণনা শুরু হবে
                    }}
                }}
                
                function typeDesc() {{
                    if (di < descStr.length) {{
                        document.getElementById('desc-{index}').innerHTML += descStr.charAt(di);
                        di++;
                        setTimeout(typeDesc, 30);
                    }}
                }}
                
                typeTitle();
            }})();
            </script>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            
            # --- ২. পুরোনো খবরগুলো নিচে সাজানো (Index 1 এবং 2) ---
            for old_idx in range(1, len(display_history)):
                old_title, old_desc = display_history[old_idx]
                st.markdown(f"""
                <div class='news-box-old'>
                    <div class='news-title-old'>➤ {old_title}</div>
                    <div class='news-desc-old'>{old_desc[:100]}...</div> 
                </div>
                """, unsafe_allow_html=True) # পুরোনো খবরের ডেসক্রিপশন কিছুটা ছোট করে দেওয়া হয়েছে
                
            st.markdown(f"<div style='color:#444; text-align:right; font-size:12px; margin-top:20px;'>News {index}/10 | Source: CNBC RSS</div>", unsafe_allow_html=True)
            
        time.sleep(20) # পড়ার জন্য ২০ সেকেন্ড সময়
        
    with main_area.container():
        st.markdown("<h3 style='color:#00FF00; text-align:center; padding: 50px 0;'>🔄 Syncing New Headlines...</h3>", unsafe_allow_html=True)
    time.sleep(3)
            
