"""
Market data service with async support and caching.
@SPEC:IMPROVE-001 REQ-PERF-001
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import yfinance as yf
import pandas as pd
import structlog

from app.services.cache import get_cache, cached

logger = structlog.get_logger(__name__)


class MarketDataService:
    """
    Service for fetching market data with async support and caching.
    @SPEC:IMPROVE-001 REQ-PERF-001
    """

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize market data service.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self._cache = get_cache()
        self._cache_ttl = cache_ttl
        logger.info("Market data service initialized", cache_ttl=cache_ttl)

    @cached(ttl=300, key_prefix='ticker_data')
    def get_ticker_data(
        self,
        ticker: str,
        period: str = "5d"
    ) -> Optional[Dict[str, Any]]:
        """
        Get historical data for a single ticker.

        Args:
            ticker: Stock ticker symbol
            period: Time period (e.g., "5d", "1mo", "1y")

        Returns:
            Dictionary with ticker data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                logger.warning("No data found for ticker", ticker=ticker)
                return None

            data = {
                'ticker': ticker,
                'current_price': float(hist['Close'].iloc[-1]),
                'previous_price': float(hist['Close'].iloc[-2]) if len(hist) >= 2 else None,
                'high': float(hist['High'].iloc[-1]),
                'low': float(hist['Low'].iloc[-1]),
                'open': float(hist['Open'].iloc[-1]),
                'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
            }

            # Calculate change
            if data['previous_price']:
                data['change'] = data['current_price'] - data['previous_price']
                data['change_pct'] = (data['change'] / data['previous_price']) * 100
            else:
                data['change'] = 0
                data['change_pct'] = 0

            logger.debug(
                "Fetched ticker data",
                ticker=ticker,
                price=data['current_price']
            )

            return data

        except Exception as e:
            logger.error(
                "Error fetching ticker data",
                ticker=ticker,
                error=str(e)
            )
            return None

    def get_ticker_data_batch(
        self,
        tickers: List[str],
        period: str = "5d"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get historical data for multiple tickers using batch download.
        @SPEC:IMPROVE-001 REQ-PERF-001

        Args:
            tickers: List of stock ticker symbols
            period: Time period

        Returns:
            Dictionary mapping tickers to their data
        """
        results = {}

        try:
            # Use yfinance batch download for efficiency
            data = yf.download(tickers, period=period, progress=False)

            if data.empty:
                logger.warning("No data found for batch", tickers=tickers)
                return results

            closes = data['Close']

            for ticker in tickers:
                try:
                    if isinstance(closes, pd.DataFrame):
                        if ticker in closes.columns:
                            prices = closes[ticker]
                        else:
                            continue
                    else:
                        prices = closes

                    if len(prices) >= 2 and not pd.isna(prices.iloc[-1]):
                        current = float(prices.iloc[-1])
                        prev = float(prices.iloc[-2]) if len(prices) >= 2 else current

                        results[ticker] = {
                            'ticker': ticker,
                            'current_price': current,
                            'previous_price': prev,
                            'change': current - prev,
                            'change_pct': ((current - prev) / prev) * 100 if prev != 0 else 0,
                        }
                except Exception as e:
                    logger.debug(
                        "Error processing ticker in batch",
                        ticker=ticker,
                        error=str(e)
                    )
                    continue

            logger.info(
                "Batch fetch completed",
                requested=len(tickers),
                retrieved=len(results)
            )

        except Exception as e:
            logger.error(
                "Error in batch fetch",
                error=str(e),
                tickers=tickers
            )

        return results

    async def get_ticker_data_async(
        self,
        ticker: str,
        period: str = "5d"
    ) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for get_ticker_data.

        Note: yfinance itself is synchronous, this wraps it for async usage.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.get_ticker_data(ticker, period)
        )

    async def get_multiple_tickers_async(
        self,
        tickers: List[str],
        period: str = "5d"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data for multiple tickers concurrently.
        @SPEC:IMPROVE-001 REQ-PERF-001

        Args:
            tickers: List of ticker symbols
            period: Time period

        Returns:
            Dictionary mapping tickers to their data
        """
        # Use batch download for better performance
        return self.get_ticker_data_batch(tickers, period)

    @cached(ttl=300, key_prefix='sector_info')
    def get_sector_info(self, ticker: str) -> str:
        """
        Get sector information for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Sector abbreviation or "-" if not found
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', '')

            sector_map = {
                'Technology': 'Tech',
                'Information Technology': 'Tech',
                'Healthcare': 'Health',
                'Health Care': 'Health',
                'Financials': 'Fin',
                'Financial Services': 'Fin',
                'Consumer Discretionary': 'Cons',
                'Consumer Cyclical': 'Cons',
                'Consumer Staples': 'Staple',
                'Consumer Defensive': 'Staple',
                'Energy': 'Energy',
                'Industrials': 'Indust',
                'Materials': 'Mater',
                'Basic Materials': 'Mater',
                'Utilities': 'Util',
                'Real Estate': 'REIT',
                'Communication Services': 'Comm',
            }

            short_sector = sector_map.get(sector, sector[:5] if sector else '-')
            return short_sector

        except Exception as e:
            logger.debug(
                "Error fetching sector info",
                ticker=ticker,
                error=str(e)
            )
            return '-'

    def get_index_data(
        self,
        indices: Optional[List[Tuple[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get data for market indices.

        Args:
            indices: List of (symbol, name) tuples. Uses defaults if not provided.

        Returns:
            List of index data dictionaries
        """
        if indices is None:
            indices = [
                ('^GSPC', 'S&P 500'),
                ('^IXIC', 'NASDAQ'),
                ('^DJI', 'Dow Jones'),
                ('^RUT', 'Russell 2000'),
            ]

        results = []

        for symbol, name in indices:
            data = self.get_ticker_data(symbol)
            if data:
                results.append({
                    'name': name,
                    'symbol': symbol,
                    'price': round(data['current_price'], 2),
                    'change': round(data['change_pct'], 2),
                })
            else:
                # Include with zero values if fetch failed
                results.append({
                    'name': name,
                    'symbol': symbol,
                    'price': 0,
                    'change': 0,
                })

        return results
