# Common tickers for suggestions
POPULAR_TICKERS = {
    "US Stocks": [
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", "AMD", "NFLX", "INTC", 
        "JPM", "BAC", "WMT", "DIS", "KO", "PEP", "XOM", "CVX", "PFE", "JNJ"
    ],
    "Crypto": [
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", 
        "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "LINK-USD"
    ],
    "Forex": [
        "EURUSD=X", "JPY=X", "GBPUSD=X", "AUDUSD=X", "NZDUSD=X", 
        "EURJPY=X", "GBPJPY=X", "EURGBP=X", "USDCAD=X", "USDCHF=X"
    ],
    "ETFs": [
        "SPY", "QQQ", "IWM", "DIA", "GLD", "SLV", "USO", "TLT", "VTI", "VOO", "ARKK", "SMH"
    ],
    "Commodities": [
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZW=F"
    ]
}

def get_all_tickers_list():
    all_tickers = []
    for category, tickers in POPULAR_TICKERS.items():
        all_tickers.extend(tickers)
    return sorted(list(set(all_tickers)))
