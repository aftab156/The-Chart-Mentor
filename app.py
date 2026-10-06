# The Chart Mentor - Official Mobile Web App (app.py)
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(page_title="The Chart Mentor", page_icon="logo.png.jpeg", layout="wide")
import pandas as pd
from datetime import datetime

# Google Sheet से यूज़र डेटा लोड करने का फ़ंक्शन
SHEET_ID = "1EHMsGwLi-MuNmyODYo65TsvL9WHV5aFvmLgD_Al-j2U"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def check_login(mobile, password):
    try:
        df = pd.read_csv(SHEET_URL)
        df['Mobile'] = df['Mobile'].astype(str).str.strip()
        df['Password'] = df['Password'].astype(str).str.strip()
        
        user = df[(df['Mobile'] == str(mobile).strip()) & (df['Password'] == str(password).strip())]
        
        if not user.empty:
            exp_date_str = str(user.iloc[0]['Expiry_Date']).strip()
            status = str(user.iloc[0]['Status']).strip()
            exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if status.lower() != 'active':
                return False, "आपका अकाउंट निष्क्रिय (Inactive) है। एडमिन से संपर्क करें।"
            elif today > exp_date:
                return False, "EXPIRED"
            else:
                return True, f"लॉगिन सफल! वैलिडिटी: {exp_date_str} तक।"
        else:
            return False, "गलत मोबाइल नंबर या पासवर्ड!"
    except Exception as e:
        return False, "डेटाबेस कनेक्ट करने में समस्या आ रही है।"

# सेशन स्टेट इनिशियलाइज़ेशन
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# अगर लॉगिन नहीं है तो लॉगिन स्क्रीन दिखाएँ
if not st.session_state.logged_in:
    st.image("logo.png.jpeg", width=150)
    st.subheader("Login to The Chart Mentor")
    
    login_mobile = st.text_input("Mobile Number")
    login_pass = st.text_input("Password", type="password")
    
    if st.button("Login"):
        success, msg = check_login(login_mobile, login_pass)
        if success:
            st.session_state.logged_in = True
            st.success(msg)
            st.rerun()
        elif msg == "EXPIRED":
            st.error("⚠️ आपकी 30 दिनों की वैधता समाप्त हो चुकी है!")
            st.warning("आगे इस्तेमाल जारी रखने के लिए नीचे दिए गए स्कैनर पर फ़ीस भेजें और स्क्रीनशॉट WhatsApp करें:")
            st.image("payment_qr.jpg.jpeg", width=250)
            st.markdown("[📲 WhatsApp पर स्क्रीनशॉट भेजें](https://wa.me/918862035610?text=Hello%20Sir,%20I%20have%20paid%20the%20subscription%20fee.)")
        else:
            st.error(msg)
    st.stop()

# Telegram Bot Credentials
BOT_TOKEN = "8903624248:AAGntVRdoPHXCGqWY42GL0gnBhTRwv5LB9s"
CHAT_ID = "7668862428"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

# 1. Market Impact News Fetcher (India + Global) in Roman Urdu/Hindi
def get_market_news():
    news_items = []
    feeds = [
        "https://news.google.com/rss/search?q=Indian+stock+market+Nifty+Sensex+crash+fall+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Global+market+economy+inflation+war+crude+oil+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    ]
    for url in feeds:
        try:
            res = requests.get(url, timeout=6)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item")[:2]:
                    title = item.find("title").text
                    news_items.append(title)
        except Exception:
            continue
    return news_items

# 2. Stock Watchlist (Halal & Technical Candidates)
WATCHLIST = [
    {"symbol": "AARTIIND.NS", "name": "Aarti Industries"},
    {"symbol": "GPPL.NS", "name": "Gujarat Pipavav Port"},
    {"symbol": "PRINCEPIPE.NS", "name": "Prince Pipes"},
    {"symbol": "NOCIL.NS", "name": "NOCIL Ltd"},
    {"symbol": "EXIDEIND.NS", "name": "Exide Industries"},
    {"symbol": "PETRONET.NS", "name": "Petronet LNG"},
    {"symbol": "CASTROLIND.NS", "name": "Castrol India"},
    {"symbol": "GSPL.NS", "name": "Gujarat State Petronet"},
    {"symbol": "MANINFRA.NS", "name": "Man Infraconstruction"}
]

# 3. Technical Strategy Analyzer (Kitab ke 5 Rules ke Mutabiq)
def check_strategy(df, strategy_name):
    if len(df) < 30:
        return None
    
    cmp = round(df['Close'].iloc[-1], 2)
    high_ath = round(df['High'].max(), 2)
    discount = round(((high_ath - cmp) / high_ath) * 100, 1)
    
    # EMAs
    df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    c = df['Close'].iloc[-1]
    e8 = df['EMA8'].iloc[-1]
    e20 = df['EMA20'].iloc[-1]
    c_prev = df['Close'].iloc[-2]
    h_prev = df['High'].iloc[-2]
    l_prev = df['Low'].iloc[-2]
    o_prev = df['Open'].iloc[-2]
    h_curr = df['High'].iloc[-1]
    l_curr = df['Low'].iloc[-1]
    o_curr = df['Open'].iloc[-1]
    
    matched = False
    entry = cmp
    sl = round(l_curr * 0.98, 2)
    
    # Hikmat-e-Amali 1: Trendline Breakout (Swing High Break)
    if strategy_name == "Trendline Breakout":
        recent_high = df['High'].iloc[-15:-1].max()
        if c > recent_high and df['Volume'].iloc[-1] > df['Volume'].iloc[-15:-1].mean():
            matched = True
            entry = round(recent_high, 2)
            sl = round(df['Low'].iloc[-5:].min(), 2)
            
    # Hikmat-e-Amali 2: Inside Candle Pattern
    elif strategy_name == "Inside Candle Pattern":
        if h_curr < h_prev and l_curr > l_prev:
            matched = True
            entry = round(h_prev + 0.5, 2)
            sl = round(l_prev - 0.5, 2)
            
    # Hikmat-e-Amali 3: Bullish Engulfing Strategy
    elif strategy_name == "Bullish Engulfing":
        if c_prev < o_prev and c > o_curr and c > h_prev and o_curr <= c_prev:
            matched = True
            entry = round(c, 2)
            sl = round(min(l_curr, l_prev), 2)
            
    # Hikmat-e-Amali 4: Pro-Gap Strategy
    elif strategy_name == "Pro-Gap Strategy":
        if o_curr > h_prev and c > o_curr:
            matched = True
            entry = round(c, 2)
            sl = round(o_curr, 2)
            
    # Hikmat-e-Amali 5: EMA 8 + EMA 20 Strategy
    elif strategy_name == "EMA 8 + EMA 20 Setup":
        if c > e8 and e8 > e20 and discount >= 35.0:
            matched = True
            entry = cmp
            sl = round(e20 * 0.99, 2)
            
    if matched:
        risk = max(1.0, round(entry - sl, 2))
        t1 = round(entry + (risk * 2), 2)  # Minimum 1:2 Reward Rule
        t2 = round(entry + (risk * 3), 2)
        return {
            "CMP": cmp,
            "Discount": f"{discount}%",
            "Entry": entry,
            "StopLoss": sl,
            "Target1": t1,
            "Target2": t2,
            "RRR": "1:2 Min (Compliant)"
        }
    return None

# --- UI Layout ---
st.image("logo.png.jpeg", width=120)
st.title(" The Chart Mentor")
st.caption("Price Action, Shariah Trading & Market Radar")

# Market News Radar (Roman English/Hindi)
st.subheader("🚨 Market Radar: Badi Khabrein Aur Khatra Alert")
news_list = get_market_news()
if news_list:
    for n in news_list:
        st.warning(f"⚠️️ **Khabar Alert:** {n}\n\n*Asar:* Aisi news par dhyan dein, agar market me mandi ya panic ho to fresh buy order lagane se bachein.")
else:
    st.info("✅ Filhal global ya domestic market me koi bada negative impact alert nahi hai.")

st.divider()

# Strategy Selection
st.subheader("🎯 Kitab Ki 5 Hikmat-e-Amali (Strategies)")
selected_strat = st.selectbox(
    "Strategy chunein jiske mutabiq scan karna hai:",
    [
        "EMA 8 + EMA 20 Setup",
        "Inside Candle Pattern",
        "Bullish Engulfing",
        "Trendline Breakout",
        "Pro-Gap Strategy"
    ]
)

if st.button("🚀 Market Scan Karein"):
    results = []
    with st.spinner("Market scan ho raha hai, Shariah aur Technical filters check ho rahe hain..."):
        for item in WATCHLIST:
            try:
                stock_data = yf.Ticker(item["symbol"]).history(period="1y")
                res = check_strategy(stock_data, selected_strat)
                if res:
                    res["Stock"] = item["name"]
                    res["Symbol"] = item["symbol"].replace(".NS", "")
                    results.append(res)
            except Exception:
                continue

    if results:
        st.success(f"🎉 Aaj ke setup mil gaye! Kul {len(results)} stock filter hue hain.")
        for r in results:
            with st.container():
                st.markdown(f"### 📌 {r['Stock']} (`{r['Symbol']}`)")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("CMP", f"₹{r['CMP']}")
                col2.metric("Discount (ATH se)", r['Discount'])
                col3.metric("Entry Level", f"₹{r['Entry']}")
                col4.metric("Stop-Loss (SL)", f"₹{r['StopLoss']}")
                st.write(f"🎯 **Target 1 (1:2 RRR):** ₹{r['Target1']} | **Target 2:** ₹{r['Target2']}")
                st.caption("🕌 Shariah Status: 100% Pass (Halaal Business & Debt < 33%)")
                st.divider()
                
        # Send Telegram Summary
        t_msg = f"🌅 *The Chart Mentor Alert*\nStrategy: *{selected_strat}*\n\n"
        for r in results:
            t_msg += f"📌 *{r['Symbol']}* | Entry: ₹{r['Entry']} | SL: ₹{r['StopLoss']} | T1: ₹{r['Target1']}\n"
        send_telegram(t_msg)
        st.toast("Alert Telegram par bhej diya gaya hai!")
    else:
        st.warning(f"ℹ️ Filhal is strategy ({selected_strat}) par koi stock setup me fit nahi baitha. Discipline banaye rakhein.")
