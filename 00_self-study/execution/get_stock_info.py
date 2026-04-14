import yfinance as yf
import sys
import json

def get_stock_info(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Get historical market data
        hist = ticker.history(period="1d")
        
        if hist.empty:
            return {"error": f"No data found for symbol {ticker_symbol}"}
            
        current_price = hist['Close'].iloc[-1]
        info = ticker.info
        
        data = {
            "symbol": ticker_symbol,
            "current_price": round(current_price, 2),
            "currency": info.get("currency", "USD"),
            "longName": info.get("longName", "N/A"),
            "dayHigh": round(hist['High'].iloc[-1], 2),
            "dayLow": round(hist['Low'].iloc[-1], 2),
            "volume": int(hist['Volume'].iloc[-1]),
            "prevClose": round(info.get("regularMarketPreviousClose", 0), 2),
        }
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker symbol provided"}))
    else:
        symbol = sys.argv[1]
        result = get_stock_info(symbol)
        print(json.dumps(result, ensure_ascii=False))