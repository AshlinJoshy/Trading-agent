import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
import json
import os
from data_loader import DataLoader
from analyzer import Analyzer
from assets import get_asset_options, get_ticker_from_option
from sentiment import SentimentAnalyzer
from backtester import Backtester
from ai_analyst import AIAnalyst

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

# --- Persistent Pinned Stocks Logic ---
PINNED_FILE = "pinned_stocks.json"

def load_pinned_stocks():
    if os.path.exists(PINNED_FILE):
        try:
            with open(PINNED_FILE, "r") as f:
                return json.load(f)
        except:
            return ["AAPL", "BTC-USD", "EURUSD=X"] # Fallback
    return ["AAPL", "BTC-USD", "EURUSD=X"] # Default

def save_pinned_stocks(tickers):
    with open(PINNED_FILE, "w") as f:
        json.dump(tickers, f)

# Initialize Session State from File if not already done
if 'pinned_tickers' not in st.session_state:
    st.session_state.pinned_tickers = load_pinned_stocks()

# --- App Title ---
st.title("Real-Time Trading Analysis & Pattern Recognition")

# --- Sidebar ---
st.sidebar.header("Configuration")

# AI Configuration
st.sidebar.subheader("AI Configuration (Gemini)")
gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
gemini_model = st.sidebar.selectbox("Gemini Model", ["gemini-pro", "gemini-1.5-flash"], index=1)

# Pinned Stocks Selection
st.sidebar.subheader("Pinned / Favorites")
pinned_selection = st.sidebar.radio("Select a Pinned Stock:", ["None"] + st.session_state.pinned_tickers)

if pinned_selection != "None":
    if st.sidebar.button(f"Remove '{pinned_selection}'"):
        st.session_state.pinned_tickers.remove(pinned_selection)
        save_pinned_stocks(st.session_state.pinned_tickers) 
        st.sidebar.success(f"Removed {pinned_selection}")
        time.sleep(0.5) 
        st.rerun()

# Asset Search
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
        save_pinned_stocks(st.session_state.pinned_tickers) 
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
sentiment_analyzer = SentimentAnalyzer()
backtester = Backtester()
ai_analyst = AIAnalyst(gemini_api_key)

# Placeholder for content
placeholder = st.empty()

def render_analysis():
    with placeholder.container():
        # Fetch Data
        data_map = loader.get_realtime_data(ticker=ticker_input, interval=selected_interval)
        
        # Multi-Timeframe Check (Simple: Check 1D Trend for context)
        # Only fetch 1D if we are on a smaller timeframe
        is_higher_tf_bullish = None
        if selected_interval in ['1m', '5m', '15m', '1h']:
            data_1d_map = loader.get_realtime_data(ticker=ticker_input, interval='1d', period='1mo')
            if ticker_input in data_1d_map:
                df_1d = data_1d_map[ticker_input]
                # Simple logic: Is Close > SMA20?
                if len(df_1d) > 20:
                    last_close_1d = df_1d['Close'].iloc[-1]
                    sma20_1d = df_1d['Close'].rolling(window=20).mean().iloc[-1]
                    is_higher_tf_bullish = last_close_1d > sma20_1d

        
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

        # Confluence Check
        confluence_msg = ""
        if is_higher_tf_bullish is not None:
            if signal_type == "Bullish" and is_higher_tf_bullish:
                confluence_msg = "✅ Confluence: Daily Trend is also Bullish."
            elif signal_type == "Bearish" and not is_higher_tf_bullish:
                confluence_msg = "✅ Confluence: Daily Trend is also Bearish."
            elif signal_type != "Neutral":
                confluence_msg = "⚠️ Warning: Signal opposes Daily Trend."

        # KPI Metrics Layout
        st.subheader(f"{ticker_input} - {last_price:.2f}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Trend Forecast", f"{prediction:.2f}", delta=f"{prediction - last_price:.2f}")
        m2.metric("AI Signal", signal, delta_color="normal" if signal_type=="Neutral" else ("off" if signal_type=="Bearish" else "inverse"))
        m3.metric("Latest Pattern", latest_pattern)
        
        if confluence_msg:
            if "Warning" in confluence_msg:
                st.warning(confluence_msg)
            else:
                st.success(confluence_msg)

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

        # Layout Improvements
        fig.update_layout(
            xaxis_rangeslider_visible=False, 
            height=600, 
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="left", 
                x=0
            ),
            dragmode='pan' 
        )
        
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        }
        
        st.plotly_chart(fig, use_container_width=True, config=config)

        # --- Additional Features Tabs ---
        tab1, tab2, tab3, tab4 = st.tabs(["AI Deep Dive", "Backtest Strategy", "News Sentiment", "Raw Data"])
        
        with tab1:
            st.subheader("Gemini AI Analysis")
            if not gemini_api_key:
                st.warning("Please enter your Gemini API Key in the sidebar to use this feature.")
            else:
                if st.button("Generate Deep Dive Analysis"):
                    with st.spinner(f"Consulting {gemini_model}... (Scanning News, Financials, and Technicals)"):
                        # We pass the full df for technical context
                        analysis_result = ai_analyst.analyze_stock(ticker_input, gemini_model, df)
                        st.markdown(analysis_result)

        with tab2:
            st.subheader("Strategy Backtest (Last 50 Candles)")
            if st.button("Run Backtest"):
                with st.spinner("Running Backtest..."):
                    results = backtester.run_backtest(df)
                    if "error" in results:
                        st.error(results["error"])
                    else:
                        b1, b2, b3, b4 = st.columns(4)
                        b1.metric("Total Trades", results["total_trades"])
                        b2.metric("Win Rate", f"{results['win_rate']}%")
                        b3.metric("Avg Return", f"{results['avg_return']}%")
                        b4.metric("Total Return", f"{results['total_return']}%")
                        
                        if results['total_return'] > 0:
                            st.success("This strategy has been profitable recently.")
                        else:
                            st.warning("This strategy has been unprofitable recently. Proceed with caution.")

        with tab3:
            st.subheader("Recent News Sentiment")
            if st.button("Analyze News"):
                with st.spinner("Fetching & Analyzing News..."):
                    score, label, news_items = sentiment_analyzer.get_news_sentiment(ticker_input)
                    st.metric("Sentiment Score", f"{score:.2f}", label)
                    
                    for news in news_items:
                        with st.expander(news['title']):
                            st.write(f"**Publisher:** {news['publisher']}")
                            st.write(f"**Sentiment:** {news['polarity']:.2f}")
                            st.markdown(f"[Read Article]({news['link']})")
        
        with tab4:
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
