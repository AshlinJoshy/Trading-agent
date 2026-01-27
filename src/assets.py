# Asset Database with Names for Search
ASSET_DB = [
    # US Stocks - Tech
    {"ticker": "AAPL", "name": "Apple Inc.", "type": "Stock"},
    {"ticker": "MSFT", "name": "Microsoft Corp", "type": "Stock"},
    {"ticker": "NVDA", "name": "NVIDIA Corp", "type": "Stock"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)", "type": "Stock"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "type": "Stock"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "type": "Stock"},
    {"ticker": "META", "name": "Meta Platforms (Facebook)", "type": "Stock"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "type": "Stock"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "type": "Stock"},
    {"ticker": "INTC", "name": "Intel Corp", "type": "Stock"},
    
    # US Stocks - General
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "type": "Stock"},
    {"ticker": "BAC", "name": "Bank of America", "type": "Stock"},
    {"ticker": "WMT", "name": "Walmart Inc.", "type": "Stock"},
    {"ticker": "DIS", "name": "Walt Disney Co.", "type": "Stock"},
    {"ticker": "KO", "name": "Coca-Cola Co.", "type": "Stock"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "type": "Stock"},
    {"ticker": "XOM", "name": "Exxon Mobil Corp", "type": "Stock"},
    {"ticker": "CVX", "name": "Chevron Corp", "type": "Stock"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "type": "Stock"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "type": "Stock"},

    # Crypto
    {"ticker": "BTC-USD", "name": "Bitcoin USD", "type": "Crypto"},
    {"ticker": "ETH-USD", "name": "Ethereum USD", "type": "Crypto"},
    {"ticker": "SOL-USD", "name": "Solana USD", "type": "Crypto"},
    {"ticker": "BNB-USD", "name": "Binance Coin USD", "type": "Crypto"},
    {"ticker": "XRP-USD", "name": "XRP USD", "type": "Crypto"},
    {"ticker": "DOGE-USD", "name": "Dogecoin USD", "type": "Crypto"},
    
    # ETFs
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "type": "ETF"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "type": "ETF"},
    {"ticker": "IWM", "name": "iShares Russell 2000 ETF", "type": "ETF"},
    {"ticker": "GLD", "name": "SPDR Gold Shares", "type": "ETF"},
    {"ticker": "SLV", "name": "iShares Silver Trust", "type": "ETF"},
    {"ticker": "USO", "name": "United States Oil Fund", "type": "ETF"},
    {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond", "type": "ETF"},
    {"ticker": "ARKK", "name": "ARK Innovation ETF", "type": "ETF"},
    {"ticker": "SMH", "name": "VanEck Semiconductor ETF", "type": "ETF"},

    # Forex
    {"ticker": "EURUSD=X", "name": "EUR/USD", "type": "Forex"},
    {"ticker": "JPY=X", "name": "USD/JPY", "type": "Forex"},
    {"ticker": "GBPUSD=X", "name": "GBP/USD", "type": "Forex"},
    {"ticker": "AUDUSD=X", "name": "AUD/USD", "type": "Forex"},
    
    # Commodities
    {"ticker": "GC=F", "name": "Gold Futures", "type": "Commodity"},
    {"ticker": "SI=F", "name": "Silver Futures", "type": "Commodity"},
    {"ticker": "CL=F", "name": "Crude Oil Futures", "type": "Commodity"},
    {"ticker": "NG=F", "name": "Natural Gas Futures", "type": "Commodity"}
]

def get_asset_options():
    """
    Returns a list of formatted strings for the selectbox.
    Format: "Name (Ticker)"
    """
    options = []
    for asset in ASSET_DB:
        display_text = f"{asset['name']} ({asset['ticker']})"
        options.append(display_text)
    return sorted(options)

def get_ticker_from_option(option_str):
    """
    Extracts ticker from "Name (Ticker)".
    """
    if "(" in option_str and option_str.endswith(")"):
        return option_str.split("(")[-1].strip(")")
    return option_str # Fallback
