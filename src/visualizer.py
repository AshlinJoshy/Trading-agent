import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from data_loader import DataLoader
from analyzer import Analyzer

# Page config
st.set_page_config(page_title="Real-Time Trading Analysis", layout="wide")

st.title("Real-Time Trading Analysis & Pattern Recognition")

# Sidebar
st.sidebar.header("Configuration")
ticker_input = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, BTC-USD)", value="AAPL")
update_interval = st.sidebar.slider("Update Interval (seconds)", 5, 300, 60)
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)

# Initialize modules
loader = DataLoader(ticker_input)
analyzer = Analyzer()

# Placeholder for content
placeholder = st.empty()

def render_analysis():
    with placeholder.container():
        # Fetch Data
        data_map = loader.get_realtime_data()
        
        if ticker_input not in data_map:
            st.error(f"No data found for {ticker_input}")
            return

        df = data_map[ticker_input]
        
        # Analyze
        df = analyzer.analyze_stock(df)
        
        # Display Info
        last_price = df['Close'].iloc[-1]
        st.metric(label=f"{ticker_input} Price", value=f"{last_price:.2f}")

        # Create Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, subplot_titles=('Price & Indicators', 'Volume'),
                            row_width=[0.2, 0.7])

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'],
                                     name='OHLC'), row=1, col=1)

        # Indicators (Short/Reversal Lines - interpreting as Support/Resistance or Bands)
        # Find BB columns dynamically
        bbu_col = next((c for c in df.columns if c.startswith('BBU_')), None)
        bbl_col = next((c for c in df.columns if c.startswith('BBL_')), None)
        
        if bbu_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbu_col], line=dict(color='gray', width=1, dash='dot'), name='Upper BB (Short Line?)'), row=1, col=1)
        if bbl_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbl_col], line=dict(color='gray', width=1, dash='dot'), name='Lower BB (Reversal Line?)'), row=1, col=1)
        
        if 'Resistance' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='red', width=1), name='Resistance (Short)'), row=1, col=1)
        if 'Support' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='green', width=1), name='Support (Reversal)'), row=1, col=1)


        # Patterns Markers
        # Filter for last N bars to avoid clutter
        recent_df = df.tail(50)
        
        # Hammer
        hammers = recent_df[recent_df['is_Hammer']]
        if not hammers.empty:
            fig.add_trace(go.Scatter(x=hammers.index, y=hammers['Low'], mode='markers', marker=dict(symbol='triangle-up', size=10, color='blue'), name='Hammer'), row=1, col=1)
            
        # Doji
        dojis = recent_df[recent_df['is_Doji']]
        if not dojis.empty:
             fig.add_trace(go.Scatter(x=dojis.index, y=dojis['High'], mode='markers', marker=dict(symbol='circle', size=8, color='yellow'), name='Doji'), row=1, col=1)
             
        # Bullish Engulfing
        engulfing = recent_df[recent_df['is_Bullish_Engulfing']]
        if not engulfing.empty:
             fig.add_trace(go.Scatter(x=engulfing.index, y=engulfing['Low'], mode='markers', marker=dict(symbol='star', size=12, color='purple'), name='Bullish Engulfing'), row=1, col=1)


        # Volume
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, height=800)
        st.plotly_chart(fig, use_container_width=True)

        # Recent Data Table
        st.subheader("Recent Data & Signals")
        cols_to_show = ['Open', 'High', 'Low', 'Close', 'Volume', 'is_Doji', 'is_Hammer', 'is_Bullish_Engulfing']
        # Filter existing columns
        cols_to_show = [c for c in cols_to_show if c in df.columns]
        st.dataframe(df[cols_to_show].tail(10).sort_index(ascending=False))


if auto_refresh:
    while True:
        render_analysis()
        time.sleep(update_interval)
        st.rerun()
else:
    render_analysis()
    if st.button("Refresh Now"):
        st.rerun()
