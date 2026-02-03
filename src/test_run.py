from data_loader import DataLoader
from analyzer import Analyzer
import pandas as pd

def test_logic():
    print("Testing Data Loader...")
    loader = DataLoader("AAPL")
    data = loader.get_realtime_data(period="1d", interval="1m")
    
    if "AAPL" in data and not data["AAPL"].empty:
        print(f"Successfully fetched {len(data['AAPL'])} rows for AAPL.")
        df = data["AAPL"]
    else:
        print("Failed to fetch data.")
        return

    print("\nTesting Analyzer...")
    analyzer = Analyzer()
    analyzed_df = analyzer.analyze_stock(df)
    
    print("Analysis complete. Columns:")
    print(analyzed_df.columns.tolist())
    
    print("\nChecking for patterns (Last 5 rows):")
    cols = ['Close', 'is_Doji', 'is_Hammer', 'is_Bullish_Engulfing', 'Resistance', 'Support']
    print(analyzed_df[cols].tail(5))
    
    print("\nTest Complete.")

if __name__ == "__main__":
    test_logic()
