from .ubci import UBCI
import argparse
import re
import logging

def main():
    """Command-line interface for UBCI"""
    
    parser = argparse.ArgumentParser(description='UBCI(Upbit Cryptocurrency Index) Query CLI')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Set logging level (default: no logging)')
    parser.add_argument('--log-file', help='Log file path (default: logs/ubci_YYYYMMDD.log)')
    parser.add_argument('command', nargs='?', help='Command or query (e.g., market, strategy, theme, sector, UBMI, KRW-BTC)')
    parser.add_argument('index', nargs='?', help='Index code for the command (e.g., UBMI, UBSI001)')
    
    args = parser.parse_args()
    
    # Initialize UBCI manager with logging options
    manager = UBCI()

    if args.log_level:
        log_level = getattr(logging, args.log_level)
        manager.setup_logging(log_level=log_level, log_file=args.log_file)
    
    # Handle list commands
    if args.command:
        command = args.command.upper()
        index = args.index.upper() if args.index else None

        # Handle command-like arguments (market, strategy, theme, sector)
        if command in ['MARKET', 'STRATEGY', 'THEME', 'SECTOR']:
            # Define index map first
            index_map = {
                'MARKET': UBCI.MARKET_NAMES,
                'STRATEGY': UBCI.STRATEGY_NAMES,
                'THEME': UBCI.THEME_NAMES,
                'SECTOR': UBCI.SECTOR_NAMES
            }[command]
            
            if not index:
                # List all available indices for the given type
                print(f"\nAvailable {command.title()}s:")
                for code, name in index_map.items():
                    print(f"  - {code}: {name}")
                return

            # Get tickers for the specified index
            get_tickers_func = {
                'MARKET': manager.get_tickers_by_market,
                'STRATEGY': manager.get_tickers_by_strategy,
                'THEME': manager.get_tickers_by_theme,
                'SECTOR': manager.get_tickers_by_sector
            }[command]

            get_name_func = {
                'MARKET': manager.get_market_name,
                'STRATEGY': manager.get_strategy_name,
                'THEME': manager.get_theme_name,
                'SECTOR': manager.get_sector_name
            }[command]

            if index in index_map:
                tickers = get_tickers_func(index)
                if tickers:
                    name = get_name_func(index)
                    print(f"\nTickers in {command.lower()} {index} ({name}):")
                    for name, ratio in tickers:
                        print(f"  - {name} ({ratio:.2f}%)")
                else:
                    print(f"No tickers found in {command.lower()} {index}")
                return
            else:
                print(f"Invalid {command.lower()} index: {index}")
                return

        # Try as market index
        if command in manager.MARKET_NAMES:
            tickers = manager.get_tickers_by_market(command)
            if tickers:
                market_name = manager.get_market_name(command)
                print(f"\nTickers in market {command} ({market_name}):")
                for name, ratio in tickers:
                    print(f"  - {name} ({ratio:.2f}%)")
            else:
                print(f"No tickers found in market {command}")
            return
            
        # Try as sector index
        if command in manager.SECTOR_NAMES:
            tickers = manager.get_tickers_by_sector(command)
            if tickers:
                sector_name = manager.get_sector_name(command)
                print(f"\nTickers in sector {command} ({sector_name}):")
                for name, ratio in tickers:
                    print(f"  - {name} ({ratio:.2f}%)")
            else:
                print(f"No tickers found in sector {command}")
            return
            
        # Try as strategy index
        if command in manager.STRATEGY_NAMES:
            tickers = manager.get_tickers_by_strategy(command)
            if tickers:
                strategy_name = manager.get_strategy_name(command)
                print(f"\nTickers in strategy {command} ({strategy_name}):")
                for name, ratio in tickers:
                    print(f"  - {name} ({ratio:.2f}%)")
            else:
                print(f"No tickers found in strategy {command}")
            return
            
        # Try as theme index
        if command in manager.THEME_NAMES:
            tickers = manager.get_tickers_by_theme(command)
            if tickers:
                theme_name = manager.get_theme_name(command)
                print(f"\nTickers in theme {command} ({theme_name}):")
                for name, ratio in tickers:
                    print(f"  - {name} ({ratio:.2f}%)")
            else:
                print(f"No tickers found in theme {command}")
            return
            
        # Try as ticker
        if manager._validate_ticker_prefix(command):
            markets = manager.get_markets_by_ticker(command)
            strategies = manager.get_strategies_by_ticker(command)
            themes = manager.get_themes_by_ticker(command)
            sectors = manager.get_sectors_by_ticker(command)
            
            print(f"\nInformation for {command}:")
            if markets:
                print(f"Market:")
                for code, name in markets:
                    print(f"  - {code} ({name}) ")
            if strategies:
                print(f"Strategy:")
                for code, name in strategies:
                    print(f"  - {code} ({name}) ")
            if themes:
                print(f"Theme:")
                for code, name in themes:
                    print(f"  - {code} ({name}) ")
            if sectors:
                print(f"Sector:")
                for code, name in sectors:
                    print(f"  - {code} ({name}) ")
            if not any([markets, strategies, themes, sectors]):
                print("No index information found")
            return
    
    # If no query or list command is provided, show help
    parser.print_help()
    print("\nExample usage:")
    print("  ubci UBMI               # List all tickers in market UBMI")
    print("  ubci SCTIDXA            # List all tickers in sector SCTIDXA")
    print("  ubci UBSI001            # List all tickers in strategy UBSI001")
    print("  ubci THMIDX17           # List all tickers in theme THMIDX17")
    print("  ubci KRW-BTC            # Show information for ticker KRW-BTC")
    print("  ubci market             # List all available markets")
    print("  ubci market UBMI        # List all tickers in market UBMI")
    print("  ubci sector             # List all available sectors")
    print("  ubci sector UBSI001     # List all tickers in strategy UBSI001")
    print("  ubci strategy           # List all available strategies")
    print("  ubci strategy UBSI001   # List all tickers in strategy UBSI001")
    print("  ubci theme              # List all available themes")
    print("  ubci theme THMIDX17     # List all tickers in theme THMIDX17")
    

if __name__ == "__main__":
    main()