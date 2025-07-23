import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="6mo")

    if data.empty:
        st.error("આ stock symbol માટે કોઈ ડેટા મળ્યો નથી.")
        return None, None

    current_price = data['Close'].iloc[-1]
    high_52w = stock.info.get('fiftyTwoWeekHigh', 0)
    low_52w = stock.info.get('fiftyTwoWeekLow', 0)
    pe_ratio = stock.info.get('trailingPE', 'N/A')
    sector = stock.info.get('sector', 'N/A')

    target_price = round(current_price * 1.1, 2)
    stop_loss = round(current_price * 0.95, 2)

    data['RSI'] = calculate_rsi(data['Close'])
    latest_rsi = round(data['RSI'].iloc[-1], 2)
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    sma_20 = round(data['SMA20'].iloc[-1], 2)
    sma_50 = round(data['SMA50'].iloc[-1], 2)

    info = {
        "વર્તમાન ભાવ": f"₹{current_price:.2f}",
        "ટાર્ગેટ ભાવ (10%)": f"₹{target_price}",
        "સ્ટોપ લોસ (5%)": f"₹{stop_loss}",
        "52 સપ્તાહ હાઇ": f"₹{high_52w}",
        "52 સપ્તાહ લો": f"₹{low_52w}",
        "PE રેશિયો": pe_ratio,
        "સેક્ટર": sector,
        "RSI (14-દિવસ)": latest_rsi,
        "SMA (20-દિવસ)": f"₹{sma_20}",
        "SMA (50-દિવસ)": f"₹{sma_50}"
    }

    return info, data

def plot_chart(data, symbol):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data['Close'], label='Close Price', color='blue')
    ax.plot(data['SMA20'], label='SMA 20', color='orange')
    ax.plot(data['SMA50'], label='SMA 50', color='green')
    ax.set_title(f"{symbol.upper()} - ભાવ અને મૂવિંગ એવરેજ", fontsize=14)
    ax.set_xlabel("તારીખ")
    ax.set_ylabel("ભાવ")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def show_corporate_actions(stock):
    st.subheader("🏢 કોર્પોરેટ એક્શન")
    try:
        actions = stock.actions
        if actions.empty:
            st.info("કોઈ કોર્પોરેટ એક્શન મળ્યા નથી.")
        else:
            st.dataframe(actions)
    except Exception as e:
        st.error(f"કોર્પોરેટ એક્શન લાવવામાં ભૂલ: {e}")

def show_volume(data):
    st.subheader("📦 ટ્રેડિંગ વોલ્યુમ")
    try:
        volume = data['Volume'].iloc[-1]
        avg_volume = round(data['Volume'].rolling(window=20).mean().iloc[-1])
        st.markdown(f"**આજનું વોલ્યુમ:** {volume:,}")
        st.markdown(f"**20-દિવસનું સરેરાશ વોલ્યુમ:** {avg_volume:,}")
    except:
        st.info("વોલ્યુમ માહિતી પ્રાપ્ત નથી.")

# Streamlit UI
st.set_page_config(page_title="ગુજરાતી સ્ટોક એનાલાઈઝર", layout="centered")
st.title("📈 ગુજરાતી સ્ટોક ટાર્ગેટ એનાલાઈઝર")

symbol = st.text_input("NSE Symbol દાખલ કરો (જેમ કે INFY.NS, TCS.NS):")

if symbol:
    info, data = analyze_stock(symbol)

    if info:
        st.subheader("📊 વિશ્લેષણનો સાર")
        for k, v in info.items():
            st.write(f"**{k}:** {v}")

        st.subheader("📉 ભાવ ચાર્ટ અને ટેકનિકલ ઇન્ડીકેટર્સ")
        plot_chart(data, symbol)

        show_corporate_actions(yf.Ticker(symbol))
        show_volume(data)
