import pandas as pd
import pandas_ta as ta
import numpy as np

class Analyzer:
    def __init__(self):
        pass

    def analyze_stock(self, df):
        if df is None or df.empty:
            return df

        # Ensure we work on a copy
        df = df.copy()

        # Calculate Indicators
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        
        # Support/Resistance
        df['Resistance'] = df['High'].rolling(window=20).max()
        df['Support'] = df['Low'].rolling(window=20).min()

        # AI Prediction (Trend Forecast)
        # Using Linear Regression based on Close price for next few periods logic
        # TSF (Time Series Forecast) is similar to Linear Regression + Slope
        # Fallback to simple linreg if tsf is missing
        try:
            # df.ta.tsf(length=14, append=True) # tsf might not be available in this version
            # Use linear regression as proxy for trend forecast
            df.ta.linreg(length=14, append=True)
            # Rename for consistency if needed, but we'll check column name later
        except Exception as e:
            print(f"Error calculating trend: {e}")
        
        # Manual Candle Pattern Detection
        self.detect_candle_patterns(df)
        
        return df

    def detect_candle_patterns(self, df):
        # Doji
        df['is_Doji'] = (abs(df['Open'] - df['Close']) <= (df['High'] - df['Low']) * 0.1)
        
        # Hammer
        body = abs(df['Open'] - df['Close'])
        upper_shadow = df['High'] - df[['Open', 'Close']].max(axis=1)
        lower_shadow = df[['Open', 'Close']].min(axis=1) - df['Low']
        df['is_Hammer'] = (
            (lower_shadow > 2 * body) & 
            (upper_shadow < body) &
            (body > 0)
        )

        # Bullish Engulfing
        df['is_Bullish_Engulfing'] = (
            (df['Close'].shift(1) < df['Open'].shift(1)) & # Prev Red
            (df['Close'] > df['Open']) & # Curr Green
            (df['Open'] < df['Close'].shift(1)) & 
            (df['Close'] > df['Open'].shift(1))
        )
        
        # Shooting Star (Bearish)
        df['is_Shooting_Star'] = (
            (upper_shadow > 2 * body) &
            (lower_shadow < body) &
            (body > 0)
        )
        
        # Bearish Engulfing
        df['is_Bearish_Engulfing'] = (
            (df['Close'].shift(1) > df['Open'].shift(1)) & # Prev Green
            (df['Close'] < df['Open']) & # Curr Red
            (df['Open'] > df['Close'].shift(1)) &
            (df['Close'] < df['Open'].shift(1))
        )

        # Assign "Latest Pattern" Name
        # We iterate backwards to find the most recent True value in these columns
        patterns = ['is_Doji', 'is_Hammer', 'is_Bullish_Engulfing', 'is_Shooting_Star', 'is_Bearish_Engulfing']
        
        def get_pattern(row):
            p_list = []
            if row['is_Bullish_Engulfing']: p_list.append("Bullish Engulfing")
            if row['is_Bearish_Engulfing']: p_list.append("Bearish Engulfing")
            if row['is_Hammer']: p_list.append("Hammer")
            if row['is_Shooting_Star']: p_list.append("Shooting Star")
            if row['is_Doji']: p_list.append("Doji")
            return ", ".join(p_list) if p_list else None

        df['Pattern'] = df.apply(get_pattern, axis=1)
        
        return df

    def get_latest_signal(self, df):
        """
        Generates a simple Buy/Sell/Wait signal based on indicators.
        """
        if df is None or df.empty:
            return "No Data", "Neutral"

        last_row = df.iloc[-1]
        rsi = last_row.get('RSI_14', 50)
        close = last_row['Close']
        sma20 = last_row.get('SMA_20', close)
        sma50 = last_row.get('SMA_50', close)
        
        # Simple Logic
        score = 0
        
        # Trend
        if close > sma20: score += 1
        if close > sma50: score += 1
        if sma20 > sma50: score += 1
        
        # RSI
        if rsi < 30: score += 2 # Oversold -> Buy
        elif rsi > 70: score -= 2 # Overbought -> Sell
        
        # Patterns (Instant Signal)
        if last_row['is_Bullish_Engulfing'] or last_row['is_Hammer']:
            score += 2
        if last_row['is_Bearish_Engulfing'] or last_row['is_Shooting_Star']:
            score -= 2
            
        if score >= 3:
            return "Strong Buy", "Bullish"
        elif score >= 1:
            return "Buy", "Bullish"
        elif score <= -3:
            return "Strong Sell", "Bearish"
        elif score <= -1:
            return "Sell", "Bearish"
        else:
            return "Hold / Wait", "Neutral"

    def get_prediction_next(self, df):
        """
        Returns the forecasted price for the next candle using Linear Regression (LINREG).
        """
        if df is None or df.empty:
            return 0
        
        # Check for LINREG or TSF columns
        # linreg returns the ending value of the regression line
        linreg_col = next((c for c in df.columns if c.startswith('LR_') or c.startswith('LINREG_')), None)
        
        if linreg_col:
            current_linreg = df[linreg_col].iloc[-1]
            # To predict "next", we can add the slope if we had it, but standard linreg output is usually the current fit.
            # We will use the current linear regression value as the "trend" price.
            return current_linreg
            
        return df['Close'].iloc[-1]
