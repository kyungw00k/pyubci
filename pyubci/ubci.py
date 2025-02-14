import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests


class UBCI:
    # API base URLs
    BASE_URL = "https://ubci-api.ubcindex.com/v1/crix/index/baskets"

    # Market index names mapping
    MARKET_NAMES = {
        "UBMI": "UBMI",
        "UBAI": "UBAI",
        "UTTI": "UBMI 10",
        "UBAI_ST": "UBAI BTC quote",
        "UBMI_ST": "UBMI BTC quote",
        "UTHI": "UBMI 30"
    }

    # Sector names mapping
    SECTOR_NAMES = {
        "SCTIDXA": "Infrastructure",
        "SCTIDXA01": "Payment Infrastructure",
        "SCTIDXA02": "Network Infrastructure",
        "SCTIDXA02-01": "Interoperability/Bridges",
        "SCTIDXA02-02": "Enterprise Blockchain",
        "SCTIDXA03": "DApp Infrastructure",
        "SCTIDXA03-01": "Oracle",
        "SCTIDXA04": "User Infrastructure",
        "SCTIDXA04-01": "DID",
        "SCTIDXA04-02": "Medical",
        "SCTIDXA04-03": "Wallet/Messaging",
        "SCTIDXA05": "DePIN",
        "SCTIDXA05-01": "AI",
        "SCTIDXA05-02": "Data Infrastructure",
        "SCTIDXA05-03": "Storage",
        "SCTIDXB": "Smart Contract Platforms",
        "SCTIDXB01": "Monolithic Blockchain",
        "SCTIDXB02": "Modular Blockchain",
        "SCTIDXC": "DeFi",
        "SCTIDXC01": "Stablecoin Group",
        "SCTIDXC01-01": "Stablecoins",
        "SCTIDXC02": "Exchange",
        "SCTIDXC02-01": "DEX/Aggregator",
        "SCTIDXC03": "Deposit",
        "SCTIDXC03-01": "Lending",
        "SCTIDXD": "Culture/Entertainment",
        "SCTIDXD01": "Virtual World",
        "SCTIDXD01-01": "Metaverse",
        "SCTIDXD01-02": "NFT/Gaming",
        "SCTIDXD02": "Content",
        "SCTIDXD02-02": "Advertising",
        "SCTIDXD02-03": "Education/Other Content",
        "SCTIDXD03": "Community",
        "SCTIDXD03-01": "Social/DAO",
        "SCTIDXD04": "Fan Tokens",
        "SCTIDXE": "Meme"}

    # Strategy index names mapping
    STRATEGY_NAMES = {
        "UBSI001": "Momentum Top 5",
        "UBSI002": "Low Volatility Top 5",
        "UBSI003": "Contrarian Top 5",
        "UBSI004": "BTC-ETH Duo",
        "UBSI005": "Global Price Gap Low 5"
    }

    # Theme index names mapping
    THEME_NAMES = {
        "THMIDX17": "BTC Group",
        "THMIDX18": "ETH Group",
        "THMIDX24": "Upbit Staking"
    }

    @property
    def MARKET_CODES(self) -> list[str]:
        """Generate market index codes
        
        Returns:
            list[str]: List of market index codes
        """
        return [f"IDX.UPBIT.{code}" for code in self.MARKET_NAMES.keys()]

    @property
    def STRATEGY_CODES(self) -> list[str]:
        """Generate strategy index codes
        
        Returns:
            list[str]: List of strategy index codes
        """
        return [f"IDX.UPBIT.{code}" for code in self.STRATEGY_NAMES.keys()]

    @property
    def THEME_CODES(self) -> list[str]:
        """Generate theme index codes
        
        Returns:
            list[str]: List of theme index codes
        """
        return [f"IDX.UPBIT.{code}" for code in self.THEME_NAMES.keys()]

    @property
    def SECTOR_CODES(self) -> list[str]:
        """Generate sector codes from SECTOR_NAMES keys
        
        Returns:
            list[str]: List of sector codes with IDX.UPBIT prefix
        """
        return [f"IDX.UPBIT.{code}" for code in self.SECTOR_NAMES.keys()]

    def __init__(self):
        # Initialize cache for API responses
        self.api_cache: Dict[str, Dict] = {}
        self.last_update: Optional[datetime] = None
        self.cache_date: Optional[str] = None
        self.daily_cache: Dict[str, Dict] = {}
        self.index_to_tickers: Dict[str, list[str]] = {}
        self.ticker_to_sector: Dict[str, str] = {}
        self.ticker_to_strategy: Dict[str, str] = {}
        self.ticker_to_theme: Dict[str, str] = {}
        self.ticker_info: Dict[str, Dict] = {}

        # Cache file path in user's home directory
        self.cache_dir = os.path.expanduser('~/.ubci')
        self.cache_file = os.path.join(self.cache_dir, 'ubci_index_cache.json')

        # Set up logging
        self.setup_logging()

        # Create cache directory if not exists
        os.makedirs(self.cache_dir, exist_ok=True, mode=0o755)

        # Try to load cache from disk first
        if not self._load_cache_from_disk():
            # If loading fails or cache is outdated, fetch new data
            self.update_index_data()

    def setup_logging(self, log_level=None, log_file=None):
        """Configure logging settings for the UBCI instance

        Args:
            log_level (int, optional): Logging level (e.g., logging.DEBUG). If None, logging is disabled.
            log_file (str, optional): Path to log file. If None, logs are written to default location.
        """
        if not log_level:
            # If no log level is specified, disable logging
            self.logger = logging.getLogger(__name__)
            self.logger.handlers.clear()
            self.logger.addHandler(logging.NullHandler())
            return

        # Remove existing handlers
        self.logger = logging.getLogger(__name__)
        self.logger.handlers.clear()
        self.logger.propagate = False  # Don't propagate to parent loggers

        # Set log level
        self.logger.setLevel(log_level)

        # Configure log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')

        # File handler setup
        if log_file:
            log_path = log_file
        else:
            log_dir = os.path.join(self.cache_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, f"ubci_{datetime.now().strftime('%Y%m%d')}.log")

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler setup
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Log initialization message
        self.logger.info("Logging setup completed")

    def _load_cache_from_disk(self) -> bool:
        """Load cached data from disk if available and valid
        
        Returns:
            bool: True if cache was loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.cache_file):
                self.logger.debug("Cache file does not exist")
                return False

            # Check file modification time
            mtime = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
            cache_age = datetime.now() - mtime
            self.logger.debug(f"Cache file age: {cache_age.total_seconds() / 3600:.1f} hours")
            if cache_age > timedelta(days=1):
                self.logger.info("Cache file is older than 24 hours")
                return False

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # Validate cache data structure
            required_keys = ['cache_date', 'api_cache']
            if not all(key in cache_data for key in required_keys):
                self.logger.warning("Invalid cache file structure")
                return False

            # Load cache data
            self.cache_date = cache_data['cache_date']
            self.api_cache = cache_data['api_cache']
            self.last_update = datetime.now()

            # Rebuild in-memory data structures from cached API responses
            for code, data in self.api_cache.items():
                # Extract index name without prefix
                index_name = code.split('.')[-1]

                # Determine index type using name mappings
                if index_name in self.MARKET_NAMES:
                    index_type = 'market'
                elif index_name in self.STRATEGY_NAMES:
                    index_type = 'strategy'
                elif index_name in self.THEME_NAMES:
                    index_type = 'theme'
                elif index_name in self.SECTOR_NAMES:
                    index_type = 'sector'
                else:
                    continue

                # Process tickers in the response
                tickers = []
                self.logger.debug(f"Processing markets for {code}")
                for market in data.get('markets', []):
                    ticker = market['code'].split('.')[-1]
                    weight = market.get('weight', 0)
                    component_ratio = market.get('componentRatio', 0)
                    tickers.append(ticker)

                    # Initialize ticker info if not exists
                    if ticker not in self.ticker_info:
                        self.ticker_info[ticker] = {
                            'index_types': set(),
                            'index_codes': {},
                            'weights': {},
                            'component_ratios': {}
                        }

                    # Store weight and component ratio information
                    self.ticker_info[ticker]['weights'][index_name] = weight
                    self.ticker_info[ticker]['component_ratios'][index_name] = component_ratio

                    # Update ticker info
                    self.ticker_info[ticker]['index_types'].add(index_type)
                    if index_type not in self.ticker_info[ticker]['index_codes']:
                        self.ticker_info[ticker]['index_codes'][index_type] = []
                    self.ticker_info[ticker]['index_codes'][index_type].append(index_name)

                    # Update mappings based on index type
                    if index_type == 'sector':
                        if ticker not in self.ticker_to_sector:
                            self.ticker_to_sector[ticker] = []
                        self.ticker_to_sector[ticker].append(index_name)
                    elif index_type == 'strategy':
                        if ticker not in self.ticker_to_strategy:
                            self.ticker_to_strategy[ticker] = []
                        self.ticker_to_strategy[ticker].append(index_name)
                    elif index_type == 'theme':
                        if ticker not in self.ticker_to_theme:
                            self.ticker_to_theme[ticker] = []
                        self.ticker_to_theme[ticker].append(index_name)

                    # Store tickers for this index
                    if tickers:
                        self.index_to_tickers[index_name] = tickers

            self.logger.debug(
                f"Cache loaded from disk and in-memory structures rebuilt (last updated: {self.cache_date})")
            return True

        except Exception as e:
            self.logger.error(f"Error loading cache from disk: {str(e)}")
            return False

    def _save_cache_to_disk(self) -> None:
        """Save current cache data to disk"""
        try:
            cache_data = {
                'cache_date': self.cache_date,
                'api_cache': self.api_cache
            }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)

            self.logger.info(f"Cache saved to disk: {self.cache_file}")

        except Exception as e:
            self.logger.error(f"Error saving cache to disk: {str(e)}")

    def _fetch_sector_data(self, sector_code: str) -> dict:
        """Fetch data for a specific sector from the API"""
        try:
            self.logger.debug(f"Fetching data for sector: {sector_code}")
            response = requests.get(f"{self.BASE_URL}?code={sector_code}")
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"Received data for {sector_code}: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error fetching data for sector {sector_code}: {str(e)}")
            return {"markets": []}

    def update_index_data(self) -> None:
        """Update all index data (markets, strategies, themes, sectors) from APIs with daily caching"""
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Check if we already have today's data in cache
            if self.cache_date == current_date:
                self.logger.info("Using cached index data")
                return

            # Clear existing cache and mappings
            self.api_cache.clear()
            self.index_to_tickers.clear()
            self.ticker_to_sector = {}
            self.ticker_to_strategy = {}
            self.ticker_to_theme = {}
            self.ticker_info = {}

            # Process all index types
            index_types = [
                (self.MARKET_CODES, self.MARKET_NAMES, 'market'),
                (self.STRATEGY_CODES, self.STRATEGY_NAMES, 'strategy'),
                (self.THEME_CODES, self.THEME_NAMES, 'theme'),
                (self.SECTOR_CODES, self.SECTOR_NAMES, 'sector')
            ]

            for codes, names_map, index_type in index_types:
                for code in codes:
                    # Extract index name without prefix
                    index_name = code.split('.')[-1]

                    # Skip if index is not in names mapping
                    if index_name not in names_map:
                        continue

                    data = self._fetch_sector_data(code)

                    # Store raw API response in cache
                    self.api_cache[code] = data

                    # Process tickers in the response
                    tickers = []
                    self.logger.debug(f"Processing markets for {code}")
                    for market in data.get('markets', []):
                        ticker = market['code'].split('.')[-1]
                        weight = market.get('weight', 0)
                        component_ratio = market.get('componentRatio', 0)
                        tickers.append(ticker)

                        # Initialize ticker info if not exists
                        if ticker not in self.ticker_info:
                            self.ticker_info[ticker] = {
                                'index_types': set(),
                                'index_codes': {},
                                'weights': {},
                                'component_ratios': {}
                            }

                        # Store weight and component ratio information
                        self.ticker_info[ticker]['weights'][index_name] = weight
                        self.ticker_info[ticker]['component_ratios'][index_name] = component_ratio

                        # Update ticker info
                        self.ticker_info[ticker]['index_types'].add(index_type)
                        if index_type not in self.ticker_info[ticker]['index_codes']:
                            self.ticker_info[ticker]['index_codes'][index_type] = []
                        self.ticker_info[ticker]['index_codes'][index_type].append(index_name)

                        # Update mappings based on index type
                        if index_type == 'sector':
                            if ticker not in self.ticker_to_sector:
                                self.ticker_to_sector[ticker] = []
                            self.ticker_to_sector[ticker].append(index_name)
                        elif index_type == 'strategy':
                            if ticker not in self.ticker_to_strategy:
                                self.ticker_to_strategy[ticker] = []
                            self.ticker_to_strategy[ticker].append(index_name)
                        elif index_type == 'theme':
                            if ticker not in self.ticker_to_theme:
                                self.ticker_to_theme[ticker] = []
                            self.ticker_to_theme[ticker].append(index_name)

                        self.logger.debug(f"Added ticker: {ticker} for {code}")
                        self.logger.debug(f"Total tickers for {code}: {len(tickers)}")

                    # Store tickers for this index
                    if tickers:
                        self.index_to_tickers[index_name] = tickers

            # Update cache date and last update time
            self.cache_date = current_date
            self.last_update = datetime.now()

            # Clean up old cache entries (keep only last 7 days)
            self._cleanup_old_cache()

            # Save updated cache to disk
            self._save_cache_to_disk()

            self.logger.info(f"Index data updated and cached for {current_date}")

        except Exception as e:
            self.logger.error(f"Error updating index data: {str(e)}")

    def _cleanup_old_cache(self, days_to_keep: int = 7) -> None:
        """Clean up old cache entries
        
        Args:
            days_to_keep (int): Number of days of cache to keep
        """
        try:
            if not self.daily_cache:
                return

            cache_dates = sorted(self.daily_cache.keys())
            if len(cache_dates) > days_to_keep:
                dates_to_remove = cache_dates[:-days_to_keep]
                for date in dates_to_remove:
                    del self.daily_cache[date]
                self.logger.info(f"Cleaned up cache entries before {cache_dates[-days_to_keep]}")
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {str(e)}")

    def _get_index_name(self, code: str, index_type: str) -> str:
        """Get name for an index code based on its type
        
        Args:
            code (str): Index code
            index_type (str): Type of index ('market', 'strategy', 'theme', 'sector')
            
        Returns:
            str: Index name if found, original code otherwise
        """
        index_maps = {
            'market': self.MARKET_NAMES,
            'strategy': self.STRATEGY_NAMES,
            'theme': self.THEME_NAMES,
            'sector': self.SECTOR_NAMES
        }
        return index_maps.get(index_type, {}).get(code, code)

    def _validate_ticker_prefix(self, ticker: str) -> bool:
        """Validate if the ticker has a valid prefix
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC', 'BTC-ETH', 'USDT-BTC')
            
        Returns:
            bool: True if the ticker has a valid prefix, False otherwise
        """
        valid_prefixes = ['KRW-', 'BTC-', 'USDT-']
        return any(ticker.startswith(prefix) for prefix in valid_prefixes)

    def _get_raw_index_codes_by_ticker(self, ticker: str, index_type: str) -> list[str]:
        """Get raw index codes for a given ticker without formatting
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC', 'BTC-ETH', 'USDT-BTC')
            index_type (str): Type of index ('market', 'strategy', 'theme', 'sector')
            
        Returns:
            list[str]: List of raw index codes associated with the ticker
        """
        # Validate ticker prefix
        if not self._validate_ticker_prefix(ticker):
            self.logger.warning(f"Invalid ticker prefix: {ticker}")
            return []

        ticker_to_index = {
            'market': lambda t: self.ticker_info.get(t, {}).get('index_codes', {}).get('market', []),
            'strategy': lambda t: self.ticker_to_strategy.get(t, []),
            'theme': lambda t: self.ticker_to_theme.get(t, []),
            'sector': lambda t: self.ticker_to_sector.get(t, [])
        }

        index_codes = ticker_to_index.get(index_type, lambda _: [])(ticker)
        if index_type == 'market':
            index_codes = list(set(index_codes))  # Deduplicate market codes

        return index_codes

    def _get_by_ticker_generic(self, ticker: str, index_type: str) -> list[tuple[str, str]]:
        """Generic method to get index information for a given ticker
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC')
            index_type (str): Type of index ('market', 'strategy', 'theme', 'sector')
            
        Returns:
            list[tuple[str, str]]: List of tuples containing (code, name) pairs associated with the ticker
        """
        index_codes = self._get_raw_index_codes_by_ticker(ticker, index_type)
        return [(code, self._get_index_name(code, index_type)) for code in index_codes]

    # ----  

    def get_market_name(self, market_code: str) -> str:
        return self._get_index_name(market_code, 'market')

    def get_strategy_name(self, strategy_code: str) -> str:
        return self._get_index_name(strategy_code, 'strategy')

    def get_theme_name(self, theme_code: str) -> str:
        return self._get_index_name(theme_code, 'theme')

    def get_sector_name(self, sector_code: str) -> str:
        return self._get_index_name(sector_code, 'sector')

    # ----  

    def get_markets_by_ticker(self, ticker: str) -> list[tuple[str, str]]:
        """Get market codes and names for a given ticker
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC')
            
        Returns:
            list[tuple[str, str]]: List of tuples containing (code, name) pairs associated with the ticker
        """
        return self._get_by_ticker_generic(ticker, 'market')

    def get_strategies_by_ticker(self, ticker: str) -> list[tuple[str, str]]:
        """Get strategy codes and names for a given ticker
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC')
            
        Returns:
            list[tuple[str, str]]: List of tuples containing (code, name) pairs associated with the ticker
        """
        return self._get_by_ticker_generic(ticker, 'strategy')

    def get_themes_by_ticker(self, ticker: str) -> list[tuple[str, str]]:
        """Get theme codes and names for a given ticker
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC')
            
        Returns:
            list[tuple[str, str]]: List of tuples containing (code, name) pairs associated with the ticker
        """
        return self._get_by_ticker_generic(ticker, 'theme')

    def get_sectors_by_ticker(self, ticker: str) -> list[tuple[str, str]]:
        """Get sector codes and names for a given ticker
        
        Args:
            ticker (str): Ticker symbol (e.g., 'KRW-BTC')
            
        Returns:
            list[tuple[str, str]]: List of tuples containing (code, name) pairs associated with the ticker
        """
        return self._get_by_ticker_generic(ticker, 'sector')

    # ----  

    def get_all_markets(self) -> list[tuple[str, str]]:
        """Get list of all available markets with names
        
        Returns:
            list[str]: List of market names
        """
        return [(code, self.get_strategy_name(code)) for code in self.MARKET_NAMES.keys()]

    def get_all_sectors(self) -> list[str]:
        """Get list of all available sectors with Korean names

        Returns:
            list[str]: List of sector names with Korean translations
        """
        return [f"{code} ({self.get_sector_name(code)})" for code in self.SECTOR_NAMES.keys()]

    def get_all_strategies(self) -> list[tuple[str, str]]:
        """Get list of all available strategies with Korean names
        
        Returns:
            list[str]: List of strategy names with Korean translations
        """
        return [(code, self.get_strategy_name(code)) for code in self.STRATEGY_NAMES.keys()]

    def get_all_themes(self) -> list[tuple[str, str]]:
        """Get list of all available themes with Korean names
        
        Returns:
            list[str]: List of theme names with Korean translations
        """
        # Filter themes based on THEME_NAMES dictionary
        theme_tickers = {theme: tickers for theme, tickers in self.index_to_tickers.items()
                         if theme in self.THEME_NAMES}
        return [(code, self.get_theme_name(code)) for code in theme_tickers.keys()]

    # ----  

    def _get_tickers_by_index_generic(self, index: str, index_type: str) -> list[tuple[str, float]]:
        """Generic method to get list of tickers in a specific index, sorted by weight and componentRatio
        
        Args:
            index (str): Index name (e.g., 'UBMI', 'UBSI001', 'THMIDX17', 'SCTIDXA')
            index_type (str): Type of index ('market', 'strategy', 'theme', 'sector')
            
        Returns:
            list[tuple[str, float]]: List of tuples containing (ticker, ratio) pairs, sorted by weight and componentRatio in descending order.
                                     The ratio is multiplied by 100 for market and sector types.
        """
        # For sectors, validate against known sector names
        if index_type == 'sector' and index not in self.SECTOR_NAMES:
            return []

        tickers = self.index_to_tickers.get(index, [])
        filtered_tickers = [ticker for ticker in tickers if
                            index_type in self.ticker_info.get(ticker, {}).get('index_types', set())
                            and index in self.ticker_info.get(ticker, {}).get('index_codes', {}).get(index_type, [])]

        # Sort tickers by weight and component ratio
        sorted_tickers = sorted(filtered_tickers,
                                key=lambda x: (self.ticker_info[x]['weights'].get(index, 0),
                                               self.ticker_info[x]['component_ratios'].get(index, 0)),
                                reverse=True)

        # Format tickers with component ratio percentage
        # Multiply by 100 for market and sector types to match existing behavior
        multiplier = 100 if index_type in ['market', 'sector'] else 1
        return [(ticker, self.ticker_info[ticker]['component_ratios'].get(index, 0) * multiplier) for ticker in
                sorted_tickers]

    def get_tickers_by_market(self, market: str) -> list[tuple[str, float]]:
        """Get list of tickers in a specific market, sorted by weight and componentRatio
        
        Args:
            market (str): Market name (e.g., 'UBMI')
            
        Returns:
            list[tuple[str, float]]: List of tuples containing (ticker, ratio) pairs, sorted by weight and componentRatio in descending order.
                                     The ratio is multiplied by 100 for market indices.
        """
        return self._get_tickers_by_index_generic(market, 'market')

    def get_tickers_by_strategy(self, strategy: str) -> list[tuple[str, float]]:
        """Get list of tickers in a specific strategy, sorted by weight and componentRatio
        
        Args:
            strategy (str): Strategy name (e.g., 'UBSI001')
            
        Returns:
            list[tuple[str, float]]: List of tuples containing (ticker, ratio) pairs, sorted by weight and componentRatio in descending order.
        """
        return self._get_tickers_by_index_generic(strategy, 'strategy')

    def get_tickers_by_theme(self, theme: str) -> list[tuple[str, float]]:
        """Get list of tickers in a specific theme, sorted by weight and componentRatio
        
        Args:
            theme (str): Theme name (e.g., 'THMIDX17')
            
        Returns:
            list[tuple[str, float]]: List of tuples containing (ticker, ratio) pairs, sorted by weight and componentRatio in descending order.
        """
        return self._get_tickers_by_index_generic(theme, 'theme')

    def get_tickers_by_sector(self, sector: str) -> list[tuple[str, float]]:
        """Get list of tickers in a specific sector, sorted by weight and componentRatio
        
        Args:
            sector (str): Sector name (e.g., 'SCTIDXA')
            
        Returns:
            list[tuple[str, float]]: List of tuples containing (ticker, ratio) pairs, sorted by weight and componentRatio in descending order.
                                     The ratio is multiplied by 100 for sector indices.
        """
        return self._get_tickers_by_index_generic(sector, 'sector')

    def get_tickers_by_index(self, index: str, index_type: str = None) -> list[str]:
        """Get list of tickers in a specific index, sorted by weight and componentRatio
        
        Args:
            index (str): Index name (e.g., 'UBMI', 'SCTIDXA')
            index_type (str, optional): Type of index ('market', 'strategy', 'theme', 'sector')
            
        Returns:
            list[str]: List of tickers in the index, sorted by weight and componentRatio in descending order
        """
        # Get tickers for the index
        filtered_tickers = self.index_to_tickers.get(index, [])

        # Sort tickers by weight and component ratio
        sorted_tickers = sorted(filtered_tickers,
                                key=lambda x: (self.ticker_info[x]['weights'].get(index, 0),
                                               self.ticker_info[x]['component_ratios'].get(index, 0)),
                                reverse=True)

        return sorted_tickers