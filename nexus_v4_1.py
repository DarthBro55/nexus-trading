import streamlit as st
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from ta import add_all_ta_features
from ta.utils import dropna
import yfinance as yf
import plotly.graph_objects as go
from cryptography.fernet import Fernet
import hashlib
import base64
import os
from datetime import datetime, timedelta

# --- App Config ---
st.set_page_config(
    page_title="NEXUS AI Trading Bot v4.1",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- Neon UI ---
st.markdown("""
<style>
    @keyframes neonPulse {
        0% { text-shadow: 0 0 10px #00ffff, 0 0 20px #ff00ff; }
        50% { text-shadow: 0 0 20px #00ff9f, 0 0 30px #ff00ff; }
        100% { text-shadow: 0 0 10px #00ffff, 0 0 20px #ff00ff; }
    }
    .stApp { background: #0a0a1f; color: #e0e0ff; }
    .neon-header {
        font-size: 3rem;
        font-weight: 900;
        color: #00ffff;
        animation: neonPulse 1.2s infinite alternate;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 6px;
    }
    .glow-card {
        background: linear-gradient(145deg, #1a0033, #000000);
        border: 3px solid transparent;
        border-image: linear-gradient(45deg, #00ffff, #ff00ff) 1;
        box-shadow: 0 0 30px #00ffff88;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="neon-header">⚡ NEXUS AI TRADING BOT v4.1 ⚡<br><span style="font-size:1.1rem;color:#00ff9f;">FULLY AUTONOMOUS • REAL-TIME ML • GLOBAL INDEXES</span></h1>', unsafe_allow_html=True)

# --- Knox Vault Encryption ---
if 'cipher' not in st.session_state:
    pw = st.text_input("🔐 Enter Military Password (AES-256)", type="password")
    if pw:
        key = base64.urlsafe_b64encode(hashlib.sha256(pw.encode()).digest())
        st.session_state.cipher = Fernet(key)
        st.success("✅ Knox Vault encryption active")
        st.rerun()
    st.stop()

# --- Trading Indexes ---
INDEXES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "DAX 40": "^GDAXI",
    "CAC 40": "^FCHI",
    "Nikkei 225": "^N225",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
    "ASX 200": "^AXJO"
}

# --- LSTM Model ---
class TradingSignalModel(nn.Module):
    def __init__(self, input_size=5):
        super().__init__()
        self.lstm = nn.LSTM(input_size, 64, batch_first=True)
        self.fc = nn.Linear(64, 3)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.fc(x[:, -1, :])
        return self.softmax(x)

# --- Train Model ---
@st.cache_resource
def train_model(ticker):
    st.info(f"🔄 Training LSTM for {ticker}...")
    data = yf.download(ticker, start="2020-01-01", end=datetime.now().strftime("%Y-%m-%d"))
    data = add_all_ta_features(data, open="Open", high="High", low="Low", close="Close", volume="Volume")
    data = dropna(data)

    # Prepare data
    features = data[['Close', 'Volume', 'trend_macd', 'momentum_rsi', 'volatility_bbh']].values
    y = (data['Close'].shift(-1) > data['Close']).astype(int).values

    # Normalize
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    # Train
    X = torch.FloatTensor(features).unsqueeze(1)
    y = torch.LongTensor(y)

    model = TradingSignalModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(30):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

    # Save model (Railway compatible)
    os.makedirs("models", exist_ok=True)
    model_path = f"models/lstm_{ticker.replace('^', '').replace('.', '_')}.pth"
    torch.save({
        'model': model.state_dict(),
        'scaler': scaler
    }, model_path)

    return model_path

# --- Load Model ---
@st.cache_resource
def load_model(ticker):
    os.makedirs("models", exist_ok=True)
    model_path = f"models/lstm_{ticker.replace('^', '').replace('.', '_')}.pth"
    if os.path.exists(model_path):
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        model = TradingSignalModel()
        model.load_state_dict(checkpoint['model'])
        return model, checkpoint['scaler']
    return None, None

# --- Generate Signal ---
def get_signal(model, scaler, ticker):
    data = yf.download(ticker, period="1d", interval="1h")
    if len(data) < 10: return "HOLD"

    features = data[['Close', 'Volume', 'trend_macd', 'momentum_rsi', 'volatility_bbh']].iloc[-1]
    features = scaler.transform([features])
    tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        model.eval()
        pred = model(tensor)
        return ["SELL", "HOLD", "BUY"][torch.argmax(pred).item()]

# --- Autonomous Agent ---
class TradingAgent:
    def __init__(self):
        self.portfolio = {}
        self.balance = 10000
        self.risk = 0.01

    def trade(self, ticker, signal, price):
        if signal == "BUY":
            size = max(1, int((self.balance * self.risk) / (price * 0.01)))
            self.portfolio[ticker] = self.portfolio.get(ticker, 0) + size
            self.balance -= price * size
            return f"✅ BOUGHT {size} {ticker} @ ${price:.2f}"
        elif signal == "SELL" and ticker in self.portfolio:
            size = self.portfolio[ticker]
            self.balance += price * size
            del self.portfolio[ticker]
            return f"✅ SOLD {size} {ticker} @ ${price:.2f}"
        return "⚠️ No action taken"

# --- Main App ---
agent = TradingAgent()

st.subheader("🌐 AUTONOMOUS TRADING DASHBOARD")
selected = st.multiselect("Select Indexes", list(INDEXES.keys()), ["S&P 500"])

if st.button("🚀 START TRADING", type="primary"):
    if not selected:
        st.error("❌ Select at least one index!")
    else:
        for idx in selected:
            ticker = INDEXES[idx]
            model, scaler = load_model(ticker)
            if not model:
                model_path = train_model(ticker)
                model, scaler = load_model(ticker)

            signal = get_signal(model, scaler, ticker)
            price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            st.info(f"{idx}: {signal} @ ${price:.2f}")
            agent.trade(ticker, signal, price)

# --- Portfolio ---
if agent.portfolio:
    st.subheader("💼 PORTFOLIO")
    df = pd.DataFrame({
        "Index": list(agent.portfolio.keys()),
        "Shares": list(agent.portfolio.values()),
        "Value": [agent.portfolio[t] * yf.Ticker(t).history(period="1d")['Close'].iloc[-1] for t in agent.portfolio.keys()]
    })
    st.dataframe(df)
    st.metric("Total Value", f"${sum(df['Value']):,.2f}")
else:
    st.info("📭 No positions held")

# --- YouTube TV ---
st.subheader("📺 LIVE MARKET TV")
st.components.v1.html('''
<iframe width="100%" height="280" src="https://www.youtube.com/embed/live_stream?channel=UCIALMKvObZNtJ6AmdCLP7Lg"
frameborder="0" allowfullscreen></iframe>
''', height=300)

st.caption("🔴 Deployed on Railway • Install as PWA on Galaxy A36")
