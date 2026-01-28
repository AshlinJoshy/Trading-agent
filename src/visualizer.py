import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from data_loader import DataLoader
from analyzer import Analyzer
from assets import get_asset_options, get_ticker_from_option

# Page config
st.set_page_config(page_title="Real-Time Trading Analysis", layout="wide")

# Custom CSS for Mobile Optimization
st.markdown("""
<style>
    /* Metric Cards Mobile Fit */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    /* Reduce padding on mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State for Pinned Stocks
if 'pinned_tickers' not in st.session_state:
    st.session_state.pinned_tickers = ["AAPL", "BTC-USD", "EURUSD=X"]

st.title("Real-Time Trading Analysis & Pattern Recognition")

# Sidebar
st.sidebar.header("Configuration")

# Pinned Stocks Logic
st.sidebar.subheader("Pinned / Favorites")
pinned_selection = st.sidebar.radio("Select a Pinned Stock:", ["None"] + st.session_state.pinned_tickers)

if pinned_selection != "None":
    if st.sidebar.button(f"Remove '{pinned_selection}'"):
        st.session_state.pinned_tickers.remove(pinned_selection)
        st.sidebar.success(f"Removed {pinned_selection}")
        time.sleep(0.5) 
        st.rerun()

# Combined Search Logic
st.sidebar.subheader("Asset Search")

asset_options = ["Type Manually / Custom"] + get_asset_options()
selected_asset_label = st.sidebar.selectbox("Search Asset (Name or Ticker):", asset_options, index=1)

if selected_asset_label == "Type Manually / Custom":
    ticker_input_val = st.sidebar.text_input("Enter Ticker Symbol:", value="AAPL")
else:
    ticker_input_val = get_ticker_from_option(selected_asset_label)

if pinned_selection != "None":
    ticker_input_val = pinned_selection

ticker_input = ticker_input_val

if st.sidebar.button("Pin Current Asset"):
    if ticker_input not in st.session_state.pinned_tickers:
        st.session_state.pinned_tickers.append(ticker_input)
        st.sidebar.success(f"Pinned {ticker_input}")


# Interval Selection
st.sidebar.subheader("Timeframe")
interval_map = {
    "1 Minute": "1m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "1 Hour": "1h",
    "1 Day": "1d",
    "1 Week": "1wk"
}
selected_interval_label = st.sidebar.selectbox("Candle Interval:", list(interval_map.keys()), index=2) 
selected_interval = interval_map[selected_interval_label]

update_interval = st.sidebar.slider("Update Speed (seconds)", 5, 300, 60)
auto_refresh = st.sidebar.checkbox("Auto Refresh Data", value=False)

# Initialize modules
loader = DataLoader(ticker_input)
analyzer = Analyzer()

# Placeholder for content
placeholder = st.empty()

def render_analysis():
    with placeholder.container():
        # Fetch Data
        data_map = loader.get_realtime_data(ticker=ticker_input, interval=selected_interval)
        
        if ticker_input not in data_map:
            st.error(f"No data found for {ticker_input} with interval {selected_interval}. Market might be closed or ticker invalid.")
            return

        df = data_map[ticker_input]
        
        # Analyze
        df = analyzer.analyze_stock(df)
        
        # Get Analysis Results
        last_price = df['Close'].iloc[-1]
        signal, signal_type, targets = analyzer.get_latest_signal(df)
        prediction = analyzer.get_prediction_next(df)
        latest_pattern = df['Pattern'].iloc[-1] if df['Pattern'].iloc[-1] else "None"

        # KPI Metrics Layout - Responsive
        # Use columns but allow them to wrap naturally or use smaller layout for mobile
        st.subheader(f"{ticker_input} - {last_price:.2f}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Trend Forecast", f"{prediction:.2f}", delta=f"{prediction - last_price:.2f}")
        m2.metric("AI Signal", signal, delta_color="normal" if signal_type=="Neutral" else ("off" if signal_type=="Bearish" else "inverse"))
        m3.metric("Latest Pattern", latest_pattern)
        
        # Trade Targets Display
        if signal_type != "Neutral":
            st.markdown(f"### 🎯 Trade Targets ({signal_type})")
            t1, t2, t3 = st.columns(3)
            t1.info(f"**Entry**: {targets['entry']:.2f}")
            t2.success(f"**Take Profit**: {targets['take_profit']:.2f}")
            t3.error(f"**Stop Loss**: {targets['stop_loss']:.2f}")
            
            if signal_type == "Bullish":
                st.success(f"**Strategy**: Long Position suggested. Target {targets['take_profit']:.2f}. Cut loss if drops below {targets['stop_loss']:.2f}.")
            else:
                st.error(f"**Strategy**: Short Position suggested. Target {targets['take_profit']:.2f}. Cover if rises above {targets['stop_loss']:.2f}.")
        else:
            st.info("Market is Neutral. No clear trade targets currently.")

        # Create Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, subplot_titles=('Price', 'Volume'),
                            row_width=[0.2, 0.7])

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'],
                                     name='OHLC'), row=1, col=1)

        # Indicators
        bbu_col = next((c for c in df.columns if c.startswith('BBU_')), None)
        bbl_col = next((c for c in df.columns if c.startswith('BBL_')), None)
        if bbu_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbu_col], line=dict(color='gray', width=1, dash='dot'), name='Upper BB'), row=1, col=1)
        if bbl_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbl_col], line=dict(color='gray', width=1, dash='dot'), name='Lower BB'), row=1, col=1)
        
        if 'Resistance' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='red', width=1), name='Resistance'), row=1, col=1)
        if 'Support' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='green', width=1), name='Support'), row=1, col=1)

        tsf_col = next((c for c in df.columns if c.startswith('TSF_') or c.startswith('LR_') or c.startswith('LINREG_')), None)
        if tsf_col:
             fig.add_trace(go.Scatter(x=df.index, y=df[tsf_col], line=dict(color='orange', width=2), name='Trend'), row=1, col=1)

        # Plot Targets if valid
        if signal_type != "Neutral" and targets['take_profit'] > 0:
             # Add horizontal lines for targets
             fig.add_hline(y=targets['take_profit'], line_dash="dash", line_color="green", annotation_text="TP", row=1, col=1)
             fig.add_hline(y=targets['stop_loss'], line_dash="dash", line_color="red", annotation_text="SL", row=1, col=1)

        # Patterns Markers
        recent_df = df.tail(100)
        bullish_mask = recent_df['is_Bullish_Engulfing'] | recent_df['is_Hammer']
        if bullish_mask.any():
            bullish_pts = recent_df[bullish_mask]
            fig.add_trace(go.Scatter(x=bullish_pts.index, y=bullish_pts['Low']*0.999, mode='markers', marker=dict(symbol='triangle-up', size=10, color='lime'), name='Bullish'), row=1, col=1)

        bearish_mask = recent_df['is_Bearish_Engulfing'] | recent_df['is_Shooting_Star']
        if bearish_mask.any():
            bearish_pts = recent_df[bearish_mask]
            fig.add_trace(go.Scatter(x=bearish_pts.index, y=bearish_pts['High']*1.001, mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Bearish'), row=1, col=1)

        # Volume
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

        # Mobile Optimized Layout
        fig.update_layout(
            xaxis_rangeslider_visible=False, 
            height=600, 
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data Table
        with st.expander("View Raw Data & Signals"):
            cols_to_show = ['Open', 'High', 'Low', 'Close', 'Volume', 'Pattern', 'RSI_14']
            cols_to_show = [c for c in cols_to_show if c in df.columns]
            st.dataframe(df[cols_to_show].tail(15).sort_index(ascending=False))

        st.caption("Data Source: Yahoo Finance. Note: Stock data may be delayed by 15 minutes. Crypto/Forex is real-time.")

if auto_refresh:
    render_analysis()
    time.sleep(update_interval)
    st.rerun()
else:
    render_analysis()
    if st.button("Refresh Now"):
        st.rerun()
