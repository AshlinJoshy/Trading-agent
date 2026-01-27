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

# Session State for Pinned Stocks
if 'pinned_tickers' not in st.session_state:
    st.session_state.pinned_tickers = ["AAPL", "BTC-USD", "EURUSD=X"]

st.title("Real-Time Trading Analysis & Pattern Recognition")

# Sidebar
st.sidebar.header("Configuration")

# Pinned Stocks Logic
st.sidebar.subheader("Pinned / Favorites")
pinned_selection = st.sidebar.radio("Select a Pinned Stock:", ["None"] + st.session_state.pinned_tickers)

# Combined Search Logic
st.sidebar.subheader("Asset Search")

# 1. Build Options List
# Start with special "Type Manually" option, then popular assets
asset_options = ["Type Manually / Custom"] + get_asset_options()

# 2. Selectbox acting as search bar
selected_asset_label = st.sidebar.selectbox("Search Asset (Name or Ticker):", asset_options, index=1)

# 3. Resolve Ticker
if selected_asset_label == "Type Manually / Custom":
    # Show text input if they chose manual
    ticker_input_val = st.sidebar.text_input("Enter Ticker Symbol:", value="AAPL")
else:
    # Extract ticker from "Name (Ticker)" string
    ticker_input_val = get_ticker_from_option(selected_asset_label)

# Override if pinned stock is selected
if pinned_selection != "None":
    ticker_input_val = pinned_selection
    # Optional: We could try to set the selectbox to match this, but it's tricky with Streamlit reruns.
    # Just showing the text input value is enough.

# Final Ticker to use
ticker_input = ticker_input_val

# Pin/Unpin Actions
col_pin, col_unpin = st.sidebar.columns(2)
if col_pin.button("Pin This"):
    if ticker_input not in st.session_state.pinned_tickers:
        st.session_state.pinned_tickers.append(ticker_input)
        st.sidebar.success(f"Pinned {ticker_input}")

if col_unpin.button("Unpin This"):
    if ticker_input in st.session_state.pinned_tickers:
        st.session_state.pinned_tickers.remove(ticker_input)
        st.sidebar.success(f"Unpinned {ticker_input}")


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
selected_interval_label = st.sidebar.selectbox("Candle Interval:", list(interval_map.keys()), index=2) # Default 15m
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
        # period logic handled inside loader based on interval
        data_map = loader.get_realtime_data(ticker=ticker_input, interval=selected_interval)
        
        if ticker_input not in data_map:
            st.error(f"No data found for {ticker_input} with interval {selected_interval}. Market might be closed or ticker invalid.")
            return

        df = data_map[ticker_input]
        
        # Analyze
        df = analyzer.analyze_stock(df)
        
        # Get Analysis Results
        last_price = df['Close'].iloc[-1]
        signal, signal_type = analyzer.get_latest_signal(df)
        prediction = analyzer.get_prediction_next(df)
        latest_pattern = df['Pattern'].iloc[-1] if df['Pattern'].iloc[-1] else "None"

        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"{ticker_input} Price", f"{last_price:.2f}")
        col2.metric("Trend Forecast (Next)", f"{prediction:.2f}", delta=f"{prediction - last_price:.2f}")
        col3.metric("AI Signal", signal, delta_color="normal" if signal_type=="Neutral" else ("off" if signal_type=="Bearish" else "inverse"))
        col4.metric("Latest Pattern", latest_pattern)
        
        if signal == "Strong Buy" or signal == "Buy":
             st.success(f"AI Suggestion: Bullish momentum detected. Consider Long position if confirmed.")
        elif signal == "Strong Sell" or signal == "Sell":
             st.error(f"AI Suggestion: Bearish pressure detected. Consider Short position or Exit.")
        else:
             st.info("AI Suggestion: Market is neutral or choppy. Wait for clearer setup.")


        # Create Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, subplot_titles=(f'{ticker_input} Price & Analysis ({selected_interval})', 'Volume'),
                            row_width=[0.2, 0.7])

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'],
                                     name='OHLC'), row=1, col=1)

        # Indicators
        # BB
        bbu_col = next((c for c in df.columns if c.startswith('BBU_')), None)
        bbl_col = next((c for c in df.columns if c.startswith('BBL_')), None)
        if bbu_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbu_col], line=dict(color='gray', width=1, dash='dot'), name='Upper Band'), row=1, col=1)
        if bbl_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbl_col], line=dict(color='gray', width=1, dash='dot'), name='Lower Band'), row=1, col=1)
        
        # Support/Resistance
        if 'Resistance' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='red', width=1), name='Resistance'), row=1, col=1)
        if 'Support' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='green', width=1), name='Support'), row=1, col=1)

        # Trend Forecast Line (TSF/Linear Reg)
        tsf_col = next((c for c in df.columns if c.startswith('TSF_') or c.startswith('LR_') or c.startswith('LINREG_')), None)
        if tsf_col:
             fig.add_trace(go.Scatter(x=df.index, y=df[tsf_col], line=dict(color='orange', width=2), name='AI Trend Line'), row=1, col=1)

        # Patterns Markers
        recent_df = df.tail(100) # Show markers only for recent history
        
        # Bullish
        bullish_mask = recent_df['is_Bullish_Engulfing'] | recent_df['is_Hammer']
        if bullish_mask.any():
            bullish_pts = recent_df[bullish_mask]
            fig.add_trace(go.Scatter(x=bullish_pts.index, y=bullish_pts['Low']*0.999, mode='markers', marker=dict(symbol='triangle-up', size=10, color='lime'), name='Bullish Pattern'), row=1, col=1)

        # Bearish
        bearish_mask = recent_df['is_Bearish_Engulfing'] | recent_df['is_Shooting_Star']
        if bearish_mask.any():
            bearish_pts = recent_df[bearish_mask]
            fig.add_trace(go.Scatter(x=bearish_pts.index, y=bearish_pts['High']*1.001, mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Bearish Pattern'), row=1, col=1)


        # Volume
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, height=700, margin=dict(l=20, r=20, t=30, b=20))
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
