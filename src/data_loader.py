import yfinance as yf
import pandas as pd
import time

class DataLoader:
    def __init__(self, tickers=None):
        # Tickers can be updated dynamically
        self.tickers = tickers if isinstance(tickers, list) else ([tickers] if tickers else [])

    def update_tickers(self, tickers):
        self.tickers = tickers if isinstance(tickers, list) else [tickers]

    def get_realtime_data(self, ticker=None, period="1d", interval="1m"):
        """
        Fetches the latest data for the tickers.
        """
        target_tickers = [ticker] if ticker else self.tickers
        data = {}
        
        # Adjust period based on interval to ensure we get enough data for indicators but not too much to be slow
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        
        # Automatic period adjustment if not specified or if 'max'/incompatible
        if interval in ['1m', '2m', '5m']:
            # 1m data is usually only available for last 7 days max, often less for free
            # '1d' or '5d' is safe
            if period not in ['1d', '5d', '7d']:
                period = '5d' 
        elif interval in ['15m', '30m', '1h', '60m']:
            if period not in ['5d', '1mo', '3mo']:
                 period = '1mo'
        elif interval in ['1d', '1wk']:
             if period == '1d':
                 period = '2y' # Need more history for daily analysis

        for t in target_tickers:
            try:
                stock = yf.Ticker(t)
                df = stock.history(period=period, interval=interval)
                if not df.empty:
                    # Clean up: Drop rows with NaN in critical columns if any
                    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
                    data[t] = df
            except Exception as e:
                print(f"Error fetching data for {t}: {e}")
        return data

    def get_ticker_info(self, ticker):
        try:
            return yf.Ticker(ticker).info
        except:
            return {}
