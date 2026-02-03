import google.generativeai as genai
import yfinance as yf
import pandas as pd

class AIAnalyst:
    def __init__(self, api_key):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)

    def analyze_stock(self, ticker, model_name, technical_df=None):
        """
        Aggregates data and sends it to Gemini for analysis.
        """
        if not self.api_key:
            return "Please provide a valid Gemini API Key."

        try:
            # 1. Gather Data
            stock = yf.Ticker(ticker)
            
            # Company Info
            info = stock.info
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            summary = info.get('longBusinessSummary', 'No summary available.')
            
            # News (Top 5)
            news = stock.news[:5] if stock.news else []
            news_text = "\n".join([f"- {n.get('title', '')} ({n.get('publisher', '')})" for n in news])

            # Financials (Last 2 years to save tokens)
            try:
                financials = stock.financials.iloc[:, :2].to_string() if not stock.financials.empty else "N/A"
            except:
                financials = "N/A"
                
            # Technical Context
            tech_summary = "No technical data provided."
            if technical_df is not None and not technical_df.empty:
                last_row = technical_df.iloc[-1]
                tech_summary = (
                    f"Price: {last_row['Close']:.2f}\n"
                    f"RSI: {last_row.get('RSI_14', 50):.2f}\n"
                    f"SMA20: {last_row.get('SMA_20', 0):.2f}\n"
                    f"SMA50: {last_row.get('SMA_50', 0):.2f}\n"
                    f"Recent Pattern: {last_row.get('Pattern', 'None')}\n"
                )

            # 2. Construct Prompt
            prompt = f"""
            You are an expert financial analyst and trader. Analyze the following data for {ticker} ({info.get('shortName', ticker)}).
            
            **Sector:** {sector} | **Industry:** {industry}
            
            **Business Summary:**
            {summary[:1000]}... (truncated)
            
            **Recent News Headlines:**
            {news_text}
            
            **Technical Indicators (Latest):**
            {tech_summary}
            
            **Recent Financials (Snapshot):**
            {financials}
            
            **Task:**
            Provide a comprehensive analysis with two distinct sections:
            
            1. **Day Trading / Short-Term Perspective:**
               - Trend analysis based on technicals.
               - Key support/resistance levels (estimate from price data provided).
               - Momentum assessment (RSI, News sentiment).
               - Verdict: Bullish, Bearish, or Neutral for today/tomorrow.
            
            2. **Long-Term Investing Perspective:**
               - Fundamental health check (based on financials/sector).
               - Growth potential and risks.
               - Verdict: Buy, Hold, or Sell for 6-12 months+.
            
            Format the output clearly using Markdown. Be professional, concise, and objective.
            """

            # 3. Call Gemini
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            return response.text

        except Exception as e:
            return f"Error during AI analysis: {str(e)}"
