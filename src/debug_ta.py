import pandas as pd
import pandas_ta as ta
import yfinance as yf

def check_ta():
    print(f"Pandas TA version: {ta.version}")
    
    df = pd.DataFrame({
        'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    })
    
    try:
        # Try to call tsf
        df.ta.tsf(length=5, append=True)
        print("TSF calculation successful")
        print(df.columns)
    except Exception as e:
        print(f"Error calling tsf: {e}")
        
    # Check if 'tsf' is in the list of indicators
    try:
        print("Available indicators:", df.ta.indicators())
    except:
        pass

if __name__ == "__main__":
    check_ta()
