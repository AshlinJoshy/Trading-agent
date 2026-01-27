# Real-Time Trading Analysis App

This application connects to stock market data (via Yahoo Finance) to provide real-time analysis, including:
- Price charts with Moving Averages and Bollinger Bands.
- Identification of "Short" (Resistance) and "Reversal" (Support) lines.
- Real-time candle pattern recognition (Doji, Hammer, Bullish Engulfing).

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Streamlit app:
    ```bash
    streamlit run src/visualizer.py
    ```

2.  Open your browser at the URL provided (usually http://localhost:8501).

3.  Enter a stock ticker (e.g., AAPL, NVDA, BTC-USD) in the sidebar.

## Structure

-   `src/data_loader.py`: Handles data fetching.
-   `src/analyzer.py`: Calculates technical indicators and patterns.
-   `src/visualizer.py`: The Streamlit dashboard.
