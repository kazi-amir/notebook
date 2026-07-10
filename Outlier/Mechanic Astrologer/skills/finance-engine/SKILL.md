---
name: finance-engine
description: Look up stock tickers, company quotes, price history, and sector leaders. Use when the user asks about stocks, stock prices, tickers, market data, company financials, ETFs, mutual funds, sector analysis, or investment research.
---

# Finance Engine

Query stock market data including ticker info, company quotes, price history, and sector leaders.

## Ticker Info

Get detailed information about a stock ticker:

```bash
# Full company profile and financials
python3 {baseDir}/finance_engine_data.py get-ticker --symbol AAPL

python3 {baseDir}/finance_engine_data.py get-ticker --symbol MSFT
```

## Company Quotes

Search for company stock quotes by name or keyword:

```bash
# Search by company name
python3 {baseDir}/finance_engine_data.py search-quotes --query "Apple"

# Search by keyword
python3 {baseDir}/finance_engine_data.py search-quotes --query "electric vehicles"
```

## Price History

Retrieve historical price data for a ticker:

```bash
# Last month of daily prices
python3 {baseDir}/finance_engine_data.py price-history --symbol AAPL --period 1mo --interval 1d

# Year-to-date weekly prices
python3 {baseDir}/finance_engine_data.py price-history --symbol TSLA --period ytd --interval 1wk

# 5-year monthly prices
python3 {baseDir}/finance_engine_data.py price-history --symbol GOOGL --period 5y --interval 1mo
```

### Period Options

| Period | Description |
|--------|-------------|
| 1d | 1 day |
| 5d | 5 days |
| 1mo | 1 month |
| 3mo | 3 months |
| 6mo | 6 months |
| 1y | 1 year |
| 2y | 2 years |
| 5y | 5 years |
| 10y | 10 years |
| ytd | Year to date |
| max | All available history |

### Interval Options

| Interval | Description |
|----------|-------------|
| 1d | Daily |
| 5d | 5-day |
| 1wk | Weekly |
| 1mo | Monthly |
| 3mo | Quarterly |

## Sector Leaders

Get top-performing companies, ETFs, or mutual funds by sector:

```bash
# Top companies in Technology
python3 {baseDir}/finance_engine_data.py get-top --sector "Technology" --top-type top_companies

# Top growth companies in Healthcare
python3 {baseDir}/finance_engine_data.py get-top --sector "Healthcare" --top-type top_growth_companies --top-n 10

# Top ETFs in Energy
python3 {baseDir}/finance_engine_data.py get-top --sector "Energy" --top-type top_etfs

# Top performing companies in Financial Services
python3 {baseDir}/finance_engine_data.py get-top --sector "Financial Services" --top-type top_performing_companies
```

### Top Type Options

| Type | Description |
|------|-------------|
| top_etfs | Leading ETFs in the sector |
| top_mutual_funds | Leading mutual funds in the sector |
| top_companies | Largest companies by market cap |
| top_growth_companies | Fastest-growing companies |
| top_performing_companies | Best-performing companies by YTD return |

### Sector Options

| Sector |
|--------|
| Basic Materials |
| Communication Services |
| Consumer Cyclical |
| Consumer Defensive |
| Energy |
| Financial Services |
| Healthcare |
| Industrials |
| Real Estate |
| Technology |
| Utilities |

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Tell me about Apple stock" | `get-ticker --symbol AAPL` |
| "What's Tesla's stock price?" | `get-ticker --symbol TSLA` |
| "Search for EV companies" | `search-quotes --query "electric vehicles"` |
| "Show me NVIDIA price history" | `price-history --symbol NVDA --period 1y --interval 1d` |
| "Top tech companies" | `get-top --sector "Technology" --top-type top_companies` |
| "Best performing energy stocks" | `get-top --sector "Energy" --top-type top_performing_companies` |
| "Growth companies in healthcare" | `get-top --sector "Healthcare" --top-type top_growth_companies` |
| "Show all finance data" | `show` |

## Data Entities

### TickerInfo

| Field | Description |
|-------|-------------|
| symbol | Ticker symbol (e.g., AAPL) |
| shortName | Short company name |
| longName | Full company name |
| sector | Business sector |
| industry | Specific industry |
| country | Country of incorporation |
| website | Company website URL |
| longBusinessSummary | Company description |
| fullTimeEmployees | Number of full-time employees |
| marketCap | Market capitalization |
| enterpriseValue | Enterprise value |
| trailingPE | Trailing price-to-earnings ratio |
| forwardPE | Forward price-to-earnings ratio |
| priceToBook | Price-to-book ratio |
| dividendYield | Dividend yield |
| beta | Stock beta (volatility relative to market) |
| fiftyTwoWeekHigh | 52-week high price |
| fiftyTwoWeekLow | 52-week low price |
| currentPrice | Current stock price |
| targetMeanPrice | Mean analyst target price |
| recommendationMean | Mean analyst recommendation (1=Strong Buy, 5=Sell) |
| numberOfAnalystOpinions | Number of analyst opinions |
| totalRevenue | Total revenue |
| revenueGrowth | Revenue growth rate |
| grossProfits | Gross profits |
| ebitda | EBITDA |
| netIncomeToCommon | Net income |
| totalCash | Total cash on hand |
| totalDebt | Total debt |
| operatingCashflow | Operating cash flow |
| freeCashflow | Free cash flow |
| auditRisk | Audit risk score (1-10) |
| boardRisk | Board risk score (1-10) |
| compensationRisk | Compensation risk score (1-10) |
| shareHolderRightsRisk | Shareholder rights risk score (1-10) |
| overallRisk | Overall governance risk score (1-10) |

### CompanyQuotes

| Field | Description |
|-------|-------------|
| company_name | Company name |
| quotes | List of stock quote entries |

### PriceHistory

| Field | Description |
|-------|-------------|
| symbol | Ticker symbol |
| entries | List of price entries |
| entries[].date | Trading date |
| entries[].open | Opening price |
| entries[].high | High price |
| entries[].low | Low price |
| entries[].close | Closing price |
| entries[].volume | Trading volume |
| entries[].dividends | Dividends paid |
| entries[].stock_splits | Stock split ratio |

### TopItem

| Field | Description |
|-------|-------------|
| symbol | Ticker symbol |
| name | Company/fund name |
| item_type | Type (company, ETF, mutual fund) |
| sector | Sector classification |
| market_cap | Market capitalization |
| market_weight | Weight in sector |
| revenue_growth | Revenue growth rate |
| earnings_growth | Earnings growth rate |
| ytd_return | Year-to-date return |
| pe_ratio | Price-to-earnings ratio |
| industry | Industry classification |
