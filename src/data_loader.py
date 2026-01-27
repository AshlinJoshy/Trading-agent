import yfinance as yf
import pandas as pd
import time

class DataLoader:
    def __init__(self, tickers):
        self.tickers = tickers if isinstance(tickers, list) else [tickers]

    def get_realtime_data(self, period="1d", interval="1m"):
        """
        Fetches the latest data for the tickers.
        For 'real-time', we usually want the last day or few days with 1m interval.
        """
        data = {}
        for ticker in self.tickers:
            try:
                # yfinance download is optimized for multiple tickers, but we loop for better error handling per ticker in this simple case
                # or use yf.download for bulk.
                # using Ticker object for more details if needed
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
                if not df.empty:
                    data[ticker] = df
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        return data

    def get_ticker_info(self, ticker):
        try:
            return yf.Ticker(ticker).info
        except:
            return {}
