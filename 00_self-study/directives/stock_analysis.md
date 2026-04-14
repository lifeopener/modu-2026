# Directive: Real-time Stock Analysis

## Goal
Provide accurate, real-time stock price and market data to the user using deterministic execution tools.

## Inputs
- `ticker_symbol` (Required): The stock symbol (e.g., 'AAPL', '005930.KS').

## Tools to Use
- `execution/get_stock_info.py`: Fetches real-time price, currency, and market high/low.

## Workflow
1. Identify the ticker symbol from the user's request.
2. Run the `execution/get_stock_info.py` script with the ticker symbol as an argument.
3. Parse the JSON output from the script.
4. If an error is returned, summarize it for the user.
5. Provide a clear, structured response including the current price, currency, and daily change.

## Edge Cases
- **Invalid Ticker**: If No data is found, ask the user to verify the ticker symbol (e.g., mention that Korean stocks need '.KS' or '.KQ').
- **Market Closed**: The price will be the latest closing price. Inform the user if the data reflects the last trading session.
