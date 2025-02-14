# pyubci
> UBCI (Upbit Crypto Index) Query Module for Python

## Overview
UBCI is a Python module that provides access to cryptocurrency indices from the UBCI(https://www.ubcindex.com). This module interfaces with the UBC Index API to fetch and manage a subset of available indices, including market indices, strategy indices, theme indices, and sector indices.

## Features
- Access to multiple index types (Market, Strategy, Theme, Sector) from UBCI
- Efficient caching mechanism with disk persistence
- Command-line interface for easy querying
- Comprehensive logging system
- Real-time data updates

## Class: UBCI

### Initialization
```python
from pyubci import UBCI

# Create UBCI instance
ubci = UBCI()
```

### Key Properties
- `MARKET_CODES`: List of market index codes
- `STRATEGY_CODES`: List of strategy index codes
- `THEME_CODES`: List of theme index codes
- `SECTOR_CODES`: List of sector index codes

### Methods

#### Data Management
- `update_index_data()`: Updates all index data from UBC Index API with daily caching
- `_load_cache_from_disk()`: Loads cached data from disk
- `_save_cache_to_disk()`: Saves current cache data to disk
- `_cleanup_old_cache(days_to_keep=7)`: Cleans up old cache entries

#### Data Retrieval
- `get_markets_by_ticker(ticker)`: Get market indices for a ticker, returns a list of tuples of (index_code, index_name)
- `get_strategies_by_ticker(ticker)`: Get strategy indices for a ticker, returns a list of tuples of (index_code, index_name)
- `get_themes_by_ticker(ticker)`: Get theme indices for a ticker, returns a list of tuples of (index_code, index_name)
- `get_sectors_by_ticker(ticker)`: Get sector indices for a ticker, returns a list of tuples of (index_code, index_name)
- `get_all_markets()`: Get all available market indices, returns a list of tuples of (index_code, index_name)
- `get_all_sectors()`: Get all available sector indices, returns a list of tuples of (index_code, index_name)
- `get_all_strategies()`: Get all available strategy indices, returns a list of tuples of (index_code, index_name)
- `get_all_themes()`: Get all available theme indices, returns a list of tuples of (index_code, index_name)
- `get_tickers_by_market(market_code)`: Get all tickers in a market index, returns a list of tuples of (ticker_name, weight)
- `get_tickers_by_strategy(strategy_code)`: Get all tickers in a strategy index, returns a list of tuples of (ticker_name, weight)
- `get_tickers_by_theme(theme_code)`: Get all tickers in a theme index, returns a list of tuples of (ticker_name, weight)
- `get_tickers_by_sector(sector_code)`: Get all tickers in a sector index, returns a list of tuples of (ticker_name, weight)

### Caching System
The UBCI module implements an efficient caching system that:
- Stores API responses locally
- Updates cache daily
- Maintains a 7-day cache history
- Persists data between sessions

## Command Line Interface

The UBCI module includes a command-line interface for easy querying:

```bash
# Direct index queries
ubci UBMI               # List all tickers in market UBMI
ubci SCTIDXA            # List all tickers in sector SCTIDXA
ubci UBSI001            # List all tickers in strategy UBSI001
ubci THMIDX17           # List all tickers in theme THMIDX17
ubci KRW-BTC            # Show information for ticker KRW-BTC

# List available indices by type
ubci market             # List all available markets
ubci market UBMI        # List all tickers in market UBMI
ubci sector             # List all available sectors
ubci sector SCTIDXA     # List all tickers in sector SCTIDXA
ubci strategy           # List all available strategies
ubci strategy UBSI001   # List all tickers in strategy UBSI001
ubci theme              # List all available themes
ubci theme THMIDX17     # List all tickers in theme THMIDX17
```

## Error Handling
The module implements comprehensive error handling:
- API request failures
- Cache read/write errors
- Invalid ticker formats
- Data validation errors

## Logging
Logging is configured with multiple handlers:
- File logging for general operations (INFO level)
- Console logging for warnings (WARNING level)
- Debug logging for detailed troubleshooting

## Best Practices
1. Initialize UBCI once and reuse the instance
2. Let the caching system handle data updates
3. Use appropriate error handling when querying data
4. Monitor logs for potential issues

## Dependencies
- requests: For API calls
- logging: For logging system
- datetime: For timestamp handling
- json: For cache serialization

## Example Usage

```python
from pyubci import UBCI

# Initialize UBCI
ubci = UBCI()

# Get market information for BTC
btc_market_indices = ubci.get_markets_by_ticker('KRW-BTC')

for index_code, index_name in btc_market_indices:
    print(f'{index_code}: {index_name}')

# Get sector information for ETH
eth_sector_indices = ubci.get_sectors_by_ticker('KRW-ETH')

```

## Notes
- The module automatically handles cache updates
- API rate limiting is handled internally
- Cache is maintained for 7 days by default
- All timestamps are in local time