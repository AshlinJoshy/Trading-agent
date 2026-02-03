import pandas as pd
from analyzer import Analyzer

class Backtester:
    def __init__(self):
        self.analyzer = Analyzer()

    def run_backtest(self, df):
        """
        Runs the current strategy on historical data (df).
        Returns: results_dict
        """
        if df is None or len(df) < 50:
            return {"error": "Not enough data"}

        # Use the Analyzer logic to generate signals on past data
        # We need to apply the same indicators first
        df = self.analyzer.analyze_stock(df)
        
        trades = []
        in_position = False
        entry_price = 0
        position_type = None # "Long" or "Short"
        
        # Simple Loop Backtest
        # We simulate walking through the data
        # Note: This is a simplified backtest (Next Open execution)
        
        for i in range(50, len(df)-1):
            row = df.iloc[i]
            next_row = df.iloc[i+1]
            
            # Re-evaluate signal logic for this historical row
            # We can't reuse get_latest_signal directly because it looks at the *last* row
            # So we reimplement the core logic inside the loop or refactor analyzer to return a signal series
            # For simplicity, let's reimplement the core score logic here to be fast
            
            score = 0
            close = row['Close']
            sma20 = row['SMA_20']
            sma50 = row['SMA_50']
            rsi = row['RSI_14']
            
            # Trend
            if close > sma20: score += 1
            if close > sma50: score += 1
            if sma20 > sma50: score += 1
            
            # RSI
            if rsi < 30: score += 2
            elif rsi > 70: score -= 2
            
            # Patterns
            if row['is_Bullish_Engulfing'] or row['is_Hammer']: score += 2
            if row['is_Bearish_Engulfing'] or row['is_Shooting_Star']: score -= 2
            
            # Entry Logic
            if not in_position:
                if score >= 3: # Strong Buy
                    entry_price = next_row['Open']
                    in_position = True
                    position_type = "Long"
                elif score <= -3: # Strong Sell
                    entry_price = next_row['Open']
                    in_position = True
                    position_type = "Short"
            
            # Exit Logic (Simple: Reversal Signal or Stop/Target)
            # Let's use a simple Exit on Signal Reversal or fixed % for MVP
            elif in_position:
                profit = 0
                exit_price = next_row['Open']
                
                if position_type == "Long":
                    if score <= -1: # Sell Signal
                        profit = (exit_price - entry_price) / entry_price
                        trades.append(profit)
                        in_position = False
                elif position_type == "Short":
                    if score >= 1: # Buy Signal
                        profit = (entry_price - exit_price) / entry_price
                        trades.append(profit)
                        in_position = False
                        
        # Compile Stats
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_return": 0,
                "total_return": 0
            }
            
        wins = [t for t in trades if t > 0]
        win_rate = (len(wins) / len(trades)) * 100
        total_return = sum(trades) * 100
        avg_return = (sum(trades) / len(trades)) * 100
        
        return {
            "total_trades": len(trades),
            "win_rate": round(win_rate, 1),
            "avg_return": round(avg_return, 2),
            "total_return": round(total_return, 2)
        }
