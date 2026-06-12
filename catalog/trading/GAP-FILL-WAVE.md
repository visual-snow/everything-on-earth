# Trading — Gap-Fill Wave

**Current catalog:** 207 repos across 15 subdomains
**Strategy:** Focus on the thinnest or noisiest buckets where the first pass likely missed canonical repos or over-indexed on thin long-tail projects.

## Targeted Subdomains

### 1. `backtesting-frameworks`
**Observed issue:** Strong top-end, but long tail is missing several canonical frameworks.

**Likely missing anchors:**
- `quantopian/zipline`
- `stefan-jansen/zipline-reloaded`
- `pmorissette/bt`
- `mhallsmoore/qstrader`
- `gbeced/pyalgotrade`

### 2. `market-data-feeds`
**Observed issue:** Count is low and the list skews toward crypto feeds.

**Likely missing anchors:**
- `ranaroussi/yfinance`
- `pydata/pandas-datareader`
- `alpacahq/marketstore`
- additional exchange or historical data collectors with reusable feed/storage layers

### 3. `quant-research-notebooks`
**Observed issue:** Count is lowest in the domain and the current set is notebook-heavy rather than research-tooling-heavy.

**Likely missing anchors:**
- `quantopian/alphalens`
- `quantopian/pyfolio`
- `quantopian/empyrical`
- `pmorissette/ffn`
- `ranaroussi/quantstats`

### 4. `sentiment-alternative-data`
**Observed issue:** First pass surfaced many small project repos and few canonical reusable libraries.

**Likely missing anchors:**
- `ProsusAI/finBERT`
- finance-specific sentiment models, StockTwits scrapers, and on-chain analytics libraries used in trading workflows

### 5. `paper-trading-simulation`
**Observed issue:** Current set contains direct simulators but is weak on paper-trading layers embedded in serious trading platforms.

**Likely missing anchors:**
- `quantconnect/lean`
- `jesse-ai/jesse`
- `nautechsystems/nautilus_trader`
- `alpacahq/alpaca-trade-api-python`
- `hummingbot/hummingbot`

## Execution Rule

Only add repos that are not already present in `catalog/trading/catalog.json` and that materially improve recall for the target subdomain.
