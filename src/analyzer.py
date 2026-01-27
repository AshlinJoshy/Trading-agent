import pandas as pd
import pandas_ta as ta

class Analyzer:
    def __init__(self):
        pass

    def analyze_stock(self, df):
        if df is None or df.empty:
            return df

        # Ensure we work on a copy to avoid SettingWithCopyWarning on the original dataframe
        df = df.copy()

        # Calculate Indicators
        # Simple Moving Averages
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        
        # RSI
        df.ta.rsi(length=14, append=True)

        # "Short" and "Reversal" lines - interpreting as Pivot Points or Support/Resistance
        # Let's use Bollinger Bands for reversal indications
        df.ta.bbands(length=20, std=2, append=True)
        
        # We can also calculate simple pivot points
        # High/Low of previous candles for resistance/support
        df['Resistance'] = df['High'].rolling(window=20).max()
        df['Support'] = df['Low'].rolling(window=20).min()

        # Identify Candle Patterns
        # We'll look for common reversal patterns
        # 'doji', 'hammer', 'hanging_man', 'shooting_star', 'engulfing'
        # pandas_ta supports "cdl_pattern"
        # patterns = df.ta.cdl_pattern(name=["doji", "hammer", "engulfing"])
        # df = pd.concat([df, patterns], axis=1) 
        
        # Note: cdl_pattern might return all 0s if no pattern found.
        # Let's add a few specific ones manually or via ta
        
        # Using the ta-lib wrapper in pandas_ta
        try:
             # This requires ta-lib binary usually, but pandas_ta has a fallback or we can implement simple ones
             # Since ta-lib binary installation failed, we might rely on simple python logic or what pandas_ta provides pure python
             # patterns = df.ta.cdl_pattern(name="all") # This often requires TA-Lib
             pass
        except Exception as e:
            print(f"Candle pattern error: {e}")

        # Manual Candle Pattern Detection (Fallback/Custom)
        self.detect_candle_patterns(df)

        return df

    def detect_candle_patterns(self, df):
        # Simple Python implementation for Hammer and Doji
        
        # Doji: Open and Close are very close
        df['is_Doji'] = (abs(df['Open'] - df['Close']) <= (df['High'] - df['Low']) * 0.1)
        
        # Hammer: Small body near top, long lower shadow
        # Body
        body = abs(df['Open'] - df['Close'])
        # Upper Shadow
        upper_shadow = df['High'] - df[['Open', 'Close']].max(axis=1)
        # Lower Shadow
        lower_shadow = df[['Open', 'Close']].min(axis=1) - df['Low']
        
        df['is_Hammer'] = (
            (lower_shadow > 2 * body) & 
            (upper_shadow < body) &
            (body > 0) # Avoid zero division or weirdness
        )

        # Engulfing (Bullish)
        # Previous red, current green, current body covers previous body
        df['is_Bullish_Engulfing'] = (
            (df['Close'].shift(1) < df['Open'].shift(1)) & # Prev Red
            (df['Close'] > df['Open']) & # Curr Green
            (df['Open'] < df['Close'].shift(1)) & 
            (df['Close'] > df['Open'].shift(1))
        )

        return df
