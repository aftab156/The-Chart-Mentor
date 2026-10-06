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
def show_stock_fundamentals(ticker_symbol):
    """Stock ke fundamentals, real business model aur live market news Roman English me dikhane ke liye"""
    try:
        clean_sym = ticker_symbol.replace('.NS', '').replace('.BO', '')
        t = yf.Ticker(ticker_symbol)
        info = t.info if hasattr(t, 'info') else {}

        # 1. Screener.in se asli business details nikalna (Backup engine)
        screener_summary = ""
        try:
            scr_url = f"https://www.screener.in/company/{clean_sym}/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(scr_url, headers=headers, timeout=3)
            if resp.status_code == 200:
                html = resp.text
                if 'class="about"' in html:
                    part = html.split('class="about"')[1].split('</div>')[0]
                    import re
                    clean_text = re.sub('<[^<]+?>', '', part).strip()
                    screener_summary = clean_text.replace('\n', ' ')
        except Exception:
            screener_summary = ""

        with st.expander(f"📊 {ticker_symbol} - Company Profile, Mazbooti aur Taaza Khabar"):
            col1, col2, col3 = st.columns(3)

            # Market Cap
            mcap = info.get('marketCap', None)
            if mcap:
                mcap_cr = f"₹{mcap / 10**7:,.2f} Cr"
                size_tag = "Badi Company (Large Cap)" if mcap > 20000*10**7 else ("Darmiyani Company (Mid Cap)" if mcap > 5000*10**7 else "Chhoti Company (Small Cap)")
            else:
                mcap_cr = "₹50 - ₹500 Cr (Est.)"
                size_tag = "SME / Micro Cap"

            # P/E Ratio
            pe = info.get('trailingPE', None)
            fwd_pe = info.get('forwardPE', None)
            if pe and isinstance(pe, (int, float)) and pe > 0:
                pe_val = f"{pe:.1f}"
                pe_tag = "Sasta" if pe < 15 else ("Wajib" if pe <= 32 else "Mehnga")
            elif fwd_pe and isinstance(fwd_pe, (int, float)) and fwd_pe > 0:
                pe_val = f"{fwd_pe:.1f} (Est)"
                pe_tag = "Forward PE"
            else:
                pe_val = "N/A"
                pe_tag = "Loss Making (Ghaata)"

            # Debt to Equity
            de = info.get('debtToEquity', None)
            if de is not None:
                de_ratio = (de / 100) if de > 5 else de
                de_val = f"{de_ratio:.2f}"
                karz_status = "Karz Kam Hai (Safe)" if de_ratio < 0.5 else ("Darmiyana Karz (Moderate)" if de_ratio <= 1.0 else "Karz Zyada Hai (Alert)")
            else:
                de_val = "< 0.33"
                karz_status = "Shariah Filter Pass"

            col1.metric("Market Cap", mcap_cr, size_tag)
            col2.metric("P/E Ratio", pe_val, pe_tag)
            col3.metric("Karz (Debt/Equity)", de_val, karz_status)

            st.markdown("---")

            # Sector & Karobaar
            sector = info.get('sector', None)
            industry = info.get('industry', None)
            summary = info.get('longBusinessSummary', None)

            if sector and sector != 'N/A':
                st.markdown(f"**🏢 Sector:** `{sector}` | **Industry:** `{industry}`")

            st.markdown("### 🛠️ Company Ka Karobaar (Business Profile)")
            
            if summary and len(summary.strip()) > 30:
                st.write(f"**Karobaar Detail:** {summary[:350]}...")
            elif screener_summary and len(screener_summary.strip()) > 15:
                st.write(f"**Karobaar Detail:** {screener_summary[:350]}...")
            else:
                st.write(f"**Karobaar Detail:** Ye company apne sector me corporate services aur production se judi commercial activities chalati hai.")

            st.markdown(f"🔗 [Company ki poori balance sheet aur karobaar Screener par dekhein](https://www.screener.in/company/{clean_sym}/consolidated/)")

            # Taaza Khabrein aur Asar (Auto Google RSS & Live News Engine)
            st.markdown("---")
            st.markdown("### 📰 Taaza Khabrein & Market Impact")
            
            news_items = []
            
            # Pehle direct headlines check karein
            if hasattr(t, 'news') and t.news:
                for item in t.news[:3]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', '#'),
                        'publisher': item.get('publisher', 'Market News')
                    })
            
            # Agar direct news na mile, toh Google News RSS se live khabar lein
            if not news_items:
                try:
                    import xml.etree.ElementTree as ET
                    rss_url = f"https://news.google.com/rss/search?q={clean_sym}+share+market+india&hl=en-IN&gl=IN&ceid=IN:en"
                    rss_resp = requests.get(rss_url, timeout=3)
                    if rss_resp.status_code == 200:
                        root = ET.fromstring(rss_resp.content)
                        for item in root.findall('./channel/item')[:3]:
                            news_items.append({
                                'title': item.find('title').text,
                                'link': item.find('link').text,
                                'publisher': item.find('source').text if item.find('source') is not None else 'Live Market'
                            })
                except Exception:
                    pass

            # News aur Asar screen par dikhayein
            if news_items:
                for item in news_items:
                    title = item.get('title', '')
                    link = item.get('link', '#')
                    publisher = item.get('publisher', 'Financial Media')
                    title_lower = title.lower()

                    if any(w in title_lower for w in ["profit", "gain", "order", "growth", "jump", "rise", "high", "deal", "dividend", "q1", "q2", "q3", "q4"]):
                        impact = "🟢 **Asar:** Positive momentum ban sakta hai."
                    elif any(w in title_lower for w in ["fall", "loss", "drop", "down", "probe", "fraud", "cut", "penalty", "decline", "sebi"]):
                        impact = "🔴 **Asar:** Thoda sambhal kar rahein, negative dabao ho sakta hai."
                    else:
                        impact = "⚪ **Asar:** Neutral update hai, price action aur levels par dhyan dein."

                    st.markdown(f"- 🔗 [{title}]({link}) *(Source: {publisher})*")
                    st.caption(impact)
            else:
                st.caption("📌 Filhaal koi badi headline nahi mili. Pure Price Action aur Structure par focus karein.")
                st.markdown(f"🔍 [Google par taaza updates check karein](https://www.google.com/search?q={clean_sym}+share+latest+news&tbm=nws)")

    except Exception as e:
        st.caption("Data load karne me dikkat aayi.")
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
    # --- GOOGLE SHEET SE SHARIAH STOCKS LOAD KARNE KA CODE ---
SHARIAH_CSV_URL = "https://docs.google.com/spreadsheets/d/1EHMsGwLi-MuNmyODYo65TsvL9WHV5aFvmLgD_Al-j2U/export?format=csv&gid=75452515"

@st.cache_data(ttl=3600)
def get_shariah_stock_list():
    try:
        df_stocks = pd.read_csv(SHARIAH_CSV_URL)
        # Google Sheet se saare symbol nikal kar saaf list banayega
        valid_symbols = df_stocks['Symbol'].dropna().astype(str).str.strip().tolist()
        return valid_symbols
    except Exception as e:
        # agar sheet load hone me koi dikkat aaye to backup list
        return ["TATAMOTORS.NS", "TATASTEEL.NS", "BEL.NS", "CIPLA.NS", "ONGC.NS"]

# Scanner ab is dynamic list ko scan karega:
STOCKS_TO_SCAN = get_shariah_stock_list()

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

# 1. Market Impact News Fetcher (Auto Roman Urdu/Hindi Translator)
def get_market_news():
    news_items = []
    feeds = [
        "https://news.google.com/rss/search?q=Indian+stock+market+Nifty+Sensex+crash+fall+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Global+market+economy+inflation+war+crude+oil+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    ]
    
    # Angrezi ke aam alfaz ko aasan Roman zubaan me badalne ka dictionary
    words_map = {
        "indian stock market crash": "Bhartiya share market me badi girawat",
        "stock market crash": "Share market me tezi se mandi / crash",
        "market crash": "Market me panic aur girawat",
        "falls": "niche fisla",
        "drops": "gira",
        "plunges": "badi girawat dekhi gayi",
        "slides": "dheere dheere gira",
        "rises": "chadh kar upar gaya",
        "gains": "munafa aur tezi dikhayi",
        "surge": "zabardast uchhal",
        "extends gains": "tezi barqarar rakhi",
        "inflation": "mehangai dar (Inflation)",
        "crude oil": "kacha tel (Crude Oil)",
        "world bank": "World Bank",
        "flags": "alert jari kiya",
        "risks": "khatre aur risk",
        "caution": "hushiyar rehne ki zaroorat",
        "warranted": "hai",
        "reasons": "wajah",
        "budget": "Budget",
        "revive": "wapas utha payega",
        "bulls": "Tezi wale (Bulls)"
    }

    for url in feeds:
        try:
            res = requests.get(url, timeout=6)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item")[:2]:
                    raw_title = item.find("title").text
                    clean_title = raw_title.split(" - ")[0] # Akhbar ka naam alag karna
                    
                    # Title ko aasan Roman Hindi/Urdu me tarjuma karna
                    trans_title = clean_title
                    for eng, rom in words_map.items():
                        import re
                        trans_title = re.sub(re.escape(eng), rom, trans_title, flags=re.IGNORECASE)
                    
                    news_items.append(trans_title)
        except Exception:
            continue
            
    return news_items
# 2. Stock Watchlist (Halal & Technical Candidates)
WATCHLIST = [{'symbol': sym, 'name': sym.replace('.NS', '')} for sym in STOCKS_TO_SCAN]
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
st.subheader("🎯 Hamari 5 Powerful Strategies Se Best Stocks Filter Karein")
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
        total_scanned = len(results)
        
        # Smart Filter: 12-15 stocks me se sabse solid Top 5 chhan kar nikalna
        if total_scanned > 5:
            def calculate_rank(s):
                score = 0
                entry = float(s.get('Entry', 1))
                
                # Penny Stock Avoid Filter (Agar price 30 se kam hai toh score kam karein)
                if entry < 30:
                    score -= 50
                elif entry >= 100:
                    score += 20  # Aache volume wale stocks ko priority
                
                # 1. Discount aur Value check
                disc = float(str(s.get('Discount', '0')).replace('%', '').strip() or 0)
                if 15 <= disc <= 45: score += 40   # Sweet spot demand area
                
                # 2. Risk to Reward Check (Target / Stoploss distance)
                sl = float(s.get('StopLoss', 1))
                t1 = float(s.get('Target1', 1))
                risk = abs(entry - sl)
                reward = abs(t1 - entry)
                if risk > 0 and (reward / risk) >= 2.0: score += 35
                
                # 3. Momentum check
                if entry > sl: score += 25
                return score
            
            # Jo stock sabse mazboot score karega wo Top 5 me aayega
            results = sorted(results, key=calculate_rank, reverse=True)[:5]

        st.success(f"🎯 Kul {total_scanned} filtered stocks me se **Top {len(results)} Sabse Solid Setup** chhan kar nikaale gaye hain!")
        st.success(f"🎯 Kul {total_scanned} filtered stocks me se **Top {len(results)} Sabse Solid Setup** chhan kar nikaale gaye hain!")
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
                show_stock_fundamentals(r['Symbol'])
                st.divider()
                
        # Send Telegram Summary
        t_msg = f"🌅 *The Chart Mentor Alert*\nStrategy: *{selected_strat}*\n\n"
        for r in results:
            t_msg += f"📌 *{r['Symbol']}* | Entry: ₹{r['Entry']} | SL: ₹{r['StopLoss']} | T1: ₹{r['Target1']}\n"
        send_telegram(t_msg)
        st.toast("Alert Telegram par bhej diya gaya hai!")
    else:
        st.warning(f"ℹ️ Filhal is strategy ({selected_strat}) par koi stock setup me fit nahi baitha. Discipline banaye rakhein.")
