"""
Market data routes for DashBoard application.
@SPEC:IMPROVE-001 REQ-ARCH-002
"""

import os
import json
import math
from flask import Blueprint, jsonify, request, render_template
import structlog

logger = structlog.get_logger(__name__)

market_bp = Blueprint('market', __name__)


# Sector mapping (moved from flask_app.py)
SECTOR_MAP = {
    "AAPL": "Tech", "MSFT": "Tech", "NVDA": "Tech", "AVGO": "Tech", "ORCL": "Tech",
    "CRM": "Tech", "AMD": "Tech", "ADBE": "Tech", "CSCO": "Tech", "INTC": "Tech",
    "JPM": "Fin", "BAC": "Fin", "WFC": "Fin", "GS": "Fin", "MS": "Fin",
    "V": "Fin", "MA": "Fin", "BRK-B": "Fin", "BLK": "Fin", "SCHW": "Fin",
    "LLY": "Health", "UNH": "Health", "JNJ": "Health", "ABBV": "Health", "MRK": "Health",
    "PFE": "Health", "TMO": "Health", "ABT": "Health", "BMY": "Health", "AMGN": "Health",
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy", "SLB": "Energy", "EOG": "Energy",
    "AMZN": "Cons", "TSLA": "Cons", "HD": "Cons", "MCD": "Cons", "NKE": "Cons",
    "WMT": "Staple", "PG": "Staple", "COST": "Staple", "KO": "Staple", "PEP": "Staple",
    "CAT": "Indust", "GE": "Indust", "HON": "Indust", "BA": "Indust", "UPS": "Indust",
    "LIN": "Mater", "APD": "Mater", "SHW": "Mater", "FCX": "Mater", "DOW": "Mater",
    "NEE": "Util", "SO": "Util", "DUK": "Util", "CEG": "Util", "SRE": "Util",
    "PLD": "REIT", "AMT": "REIT", "EQIX": "REIT", "SPG": "REIT", "O": "REIT",
    "META": "Comm", "GOOGL": "Comm", "NFLX": "Comm", "DIS": "Comm", "VZ": "Comm",
    "GOOG": "Comm", "CMCSA": "Comm", "TMUS": "Comm", "CHTR": "Comm",
}

SECTOR_CACHE_FILE = "sector_cache.json"
_sector_cache = {}


def _load_sector_cache():
    """Load sector cache from file."""
    global _sector_cache
    try:
        if os.path.exists(SECTOR_CACHE_FILE):
            with open(SECTOR_CACHE_FILE, "r", encoding="utf-8") as f:
                _sector_cache = json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        _sector_cache = {}
    return _sector_cache


def _save_sector_cache(cache):
    """Save sector cache to file."""
    try:
        with open(SECTOR_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Error saving sector cache", error=str(e))


# Initialize cache on module load
_sector_cache = _load_sector_cache()


def get_sector(ticker):
    """
    Get sector for a ticker symbol.
    @SPEC:IMPROVE-001
    """
    global _sector_cache

    if ticker in SECTOR_MAP:
        return SECTOR_MAP[ticker]
    if ticker in _sector_cache:
        return _sector_cache[ticker]

    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get("sector", "")

        sector_map = {
            "Technology": "Tech", "Information Technology": "Tech",
            "Healthcare": "Health", "Health Care": "Health",
            "Financials": "Fin", "Financial Services": "Fin",
            "Consumer Discretionary": "Cons", "Consumer Cyclical": "Cons",
            "Consumer Staples": "Staple", "Consumer Defensive": "Staple",
            "Energy": "Energy", "Industrials": "Indust",
            "Materials": "Mater", "Basic Materials": "Mater",
            "Utilities": "Util", "Real Estate": "REIT",
            "Communication Services": "Comm",
        }
        short_sector = sector_map.get(sector, sector[:5] if sector else "-")
        _sector_cache[ticker] = short_sector
        _save_sector_cache(_sector_cache)
        return short_sector
    except Exception as e:
        logger.debug("Error getting sector", ticker=ticker, error=str(e))
        _sector_cache[ticker] = "-"
        _save_sector_cache(_sector_cache)
        return "-"


@market_bp.route("/")
def index():
    """Render main index page."""
    return render_template("index.html")


@market_bp.route("/api/us/indices")
def get_us_indices():
    """
    Get major US market indices data.
    @SPEC:IMPROVE-001
    """
    try:
        import yfinance as yf

        indices_map = [
            ("^GSPC", "S&P 500"),
            ("^IXIC", "NASDAQ"),
            ("^DJI", "Dow Jones"),
            ("^RUT", "Russell 2000"),
        ]

        indices_data = []

        for symbol, name in indices_map:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="5d")

                if not hist.empty and len(hist) >= 2:
                    current_price = float(hist["Close"].iloc[-1])
                    prev_price = float(hist["Close"].iloc[-2])
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100 if prev_price != 0 else 0

                    indices_data.append({
                        "name": name,
                        "symbol": symbol,
                        "price": round(current_price, 2),
                        "change": round(change_pct, 2),
                    })
                else:
                    indices_data.append({
                        "name": name,
                        "symbol": symbol,
                        "price": 0,
                        "change": 0,
                    })
            except Exception as e:
                logger.error("Error fetching index data", symbol=symbol, error=str(e))
                indices_data.append({
                    "name": name,
                    "symbol": symbol,
                    "price": 0,
                    "change": 0,
                })

        return jsonify({"indices": indices_data})

    except Exception as e:
        logger.error("Error getting US indices data", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/portfolio")
def get_us_portfolio_data():
    """Get US portfolio data."""
    try:
        import yfinance as yf

        market_indices = []
        indices_map = {
            "^DJI": "Dow Jones",
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "BTC-USD": "Bitcoin",
            "^TNX": "10Y Treasury",
            "DX-Y.NYB": "Dollar Index",
            "KRW=X": "USD/KRW",
        }

        for ticker, name in indices_map.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty and len(hist) >= 2:
                    current_val = float(hist["Close"].iloc[-1])
                    prev_val = float(hist["Close"].iloc[-2])
                    change = current_val - prev_val
                    change_pct = (change / prev_val) * 100
                    market_indices.append({
                        "name": name,
                        "price": f"{current_val:,.2f}",
                        "change": f"{change:,.2f}",
                        "change_pct": round(change_pct, 2),
                        "color": "green" if change >= 0 else "red",
                    })
            except Exception:
                pass

        return jsonify({
            "market_indices": market_indices,
            "top_holdings": [],
            "style_box": {}
        })
    except Exception as e:
        logger.error("Error getting US portfolio data", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/smart-money")
def get_us_smart_money():
    """Get smart money picks data."""
    try:
        import yfinance as yf
        import pandas as pd

        current_file = "us_market/smart_money_current.json"
        if os.path.exists(current_file):
            with open(current_file, "r", encoding="utf-8") as f:
                snapshot = json.load(f)

            tickers = [p["ticker"] for p in snapshot["picks"]]
            current_prices = {}

            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="5d")
                    if not hist.empty:
                        current_prices[ticker] = round(float(hist["Close"].iloc[-1]), 2)
                except Exception:
                    pass

            picks_with_perf = []
            for pick in snapshot["picks"]:
                ticker = pick["ticker"]
                price_at_rec = pick.get("price_at_analysis", 0) or 0
                current_price = current_prices.get(ticker, price_at_rec) or price_at_rec or 0

                if isinstance(price_at_rec, float) and math.isnan(price_at_rec):
                    price_at_rec = 0
                if isinstance(current_price, float) and math.isnan(current_price):
                    current_price = price_at_rec
                if price_at_rec > 0:
                    change_pct = ((current_price / price_at_rec) - 1) * 100
                else:
                    change_pct = 0
                if isinstance(change_pct, float) and math.isnan(change_pct):
                    change_pct = 0

                picks_with_perf.append({
                    **pick,
                    "sector": get_sector(ticker),
                    "current_price": current_price,
                    "price_at_rec": price_at_rec,
                    "change_since_rec": round(change_pct, 2),
                })

            return jsonify({
                "analysis_date": snapshot.get("analysis_date", ""),
                "analysis_timestamp": snapshot.get("analysis_timestamp", ""),
                "top_picks": picks_with_perf,
                "summary": {
                    "total_analyzed": len(picks_with_perf),
                    "avg_score": round(
                        sum(p.get("final_score", p.get("composite_score", 0)) for p in picks_with_perf)
                        / len(picks_with_perf), 1
                    ) if picks_with_perf else 0,
                },
            })
        else:
            csv_path = "us_market/data/smart_money_picks_v2.csv"
            if not os.path.exists(csv_path):
                csv_path = "us_market/smart_money_picks_v2.csv"
            if not os.path.exists(csv_path):
                return jsonify({"error": "Smart money picks not found. Run screener first."}), 404

            df = pd.read_csv(csv_path)
            # Simplified response for CSV fallback
            top_picks = []
            for _, row in df.head(20).iterrows():
                ticker = row["ticker"]
                top_picks.append({
                    "ticker": ticker,
                    "name": row.get("name", ticker),
                    "sector": get_sector(ticker),
                    "final_score": row.get("smart_money_score", row.get("composite_score", 0)),
                    "current_price": row.get("current_price", 0),
                    "price_at_rec": row.get("current_price", 0),
                    "change_since_rec": 0,
                    "category": row.get("category", "N/A"),
                })

            return jsonify({
                "top_picks": top_picks,
                "summary": {
                    "total_analyzed": len(df),
                    "avg_score": round(df["smart_money_score"].mean() if "smart_money_score" in df.columns else 0, 1),
                },
            })
    except Exception as e:
        logger.error("Error getting smart money picks", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/etf-flows")
def get_us_etf_flows():
    """Get ETF flows data."""
    try:
        import pandas as pd

        csv_path = "us_market/data/us_etf_flows.csv"
        if not os.path.exists(csv_path):
            csv_path = "us_market/us_etf_flows.csv"
        if not os.path.exists(csv_path):
            return jsonify({"error": "ETF flows not found. Run analyze_etf_flows.py first."}), 404

        df = pd.read_csv(csv_path)
        broad_market = df[df["category"] == "Broad Market"]
        broad_score = round(broad_market["flow_score"].mean(), 1) if not broad_market.empty else 50

        sector_flows = df[df["category"] == "Sector"].to_dict(orient="records")
        top_inflows = df.nlargest(5, "flow_score").to_dict(orient="records")
        top_outflows = df.nsmallest(5, "flow_score").to_dict(orient="records")

        ai_analysis_text = ""
        ai_path = "us_market/etf_flow_analysis.json"
        if os.path.exists(ai_path):
            with open(ai_path, "r", encoding="utf-8") as f:
                ai_data = json.load(f)
                ai_analysis_text = ai_data.get("ai_analysis", "")

        return jsonify({
            "market_sentiment_score": broad_score,
            "sector_flows": sector_flows,
            "top_inflows": top_inflows,
            "top_outflows": top_outflows,
            "all_etfs": df.to_dict(orient="records"),
            "ai_analysis": ai_analysis_text,
        })
    except Exception as e:
        logger.error("Error getting ETF flows", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/stock-chart/<ticker>")
def get_us_stock_chart(ticker):
    """Get stock chart data for a ticker."""
    try:
        import yfinance as yf

        period = request.args.get("period", "1y")
        valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        if period not in valid_periods:
            period = "1y"

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return jsonify({"error": f"No data found for {ticker}"}), 404

        candles = []
        for date, row in hist.iterrows():
            candles.append({
                "time": int(date.timestamp()),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
            })

        return jsonify({"ticker": ticker, "period": period, "candles": candles})
    except Exception as e:
        logger.error("Error getting stock chart", ticker=ticker, error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/history-dates")
def get_us_history_dates():
    """Get available history dates."""
    try:
        history_dir = "us_market/history"
        if not os.path.exists(history_dir):
            return jsonify({"dates": []})

        dates = []
        for f in os.listdir(history_dir):
            if f.startswith("picks_") and f.endswith(".json"):
                date_str = f[6:-5]
                dates.append(date_str)

        dates.sort(reverse=True)
        return jsonify({"dates": dates, "count": len(dates)})
    except Exception as e:
        logger.error("Error getting history dates", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/history/<date>")
def get_us_history_by_date(date):
    """Get historical picks for a specific date."""
    try:
        import yfinance as yf

        history_file = f"us_market/history/picks_{date}.json"

        if not os.path.exists(history_file):
            return jsonify({"error": f"No analysis found for {date}"}), 404

        with open(history_file, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        tickers = [p["ticker"] for p in snapshot["picks"]]
        current_prices = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty:
                    current_prices[ticker] = round(float(hist["Close"].iloc[-1]), 2)
            except Exception:
                pass

        picks_with_perf = []
        for pick in snapshot["picks"]:
            ticker = pick["ticker"]
            price_at_rec = pick.get("price_at_analysis", 0) or 0
            current_price = current_prices.get(ticker, price_at_rec) or price_at_rec or 0

            if isinstance(price_at_rec, float) and math.isnan(price_at_rec):
                price_at_rec = 0
            if isinstance(current_price, float) and math.isnan(current_price):
                current_price = price_at_rec
            if price_at_rec > 0:
                change_pct = ((current_price / price_at_rec) - 1) * 100
            else:
                change_pct = 0
            if isinstance(change_pct, float) and math.isnan(change_pct):
                change_pct = 0

            picks_with_perf.append({
                **pick,
                "sector": get_sector(ticker),
                "current_price": current_price,
                "price_at_rec": price_at_rec,
                "change_since_rec": round(change_pct, 2),
            })

        changes = [p["change_since_rec"] for p in picks_with_perf if p["price_at_rec"] > 0]
        avg_perf = round(sum(changes) / len(changes), 2) if changes else 0

        return jsonify({
            "analysis_date": snapshot.get("analysis_date", date),
            "analysis_timestamp": snapshot.get("analysis_timestamp", ""),
            "top_picks": picks_with_perf,
            "summary": {"total": len(picks_with_perf), "avg_performance": avg_perf},
        })
    except Exception as e:
        logger.error("Error getting history by date", date=date, error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/macro-analysis")
def get_us_macro_analysis():
    """Get macro analysis data."""
    try:
        import yfinance as yf
        from datetime import datetime

        lang = request.args.get("lang", "ko")
        model = request.args.get("model", "gemini")

        macro_indicators = {}

        # Determine analysis path based on lang and model
        if model == "gpt":
            analysis_path = f"us_market/macro_analysis_gpt_{'en' if lang == 'en' else ''}.json"
            if not os.path.exists(analysis_path):
                analysis_path = f"us_market/macro_analysis_{'en' if lang == 'en' else ''}.json"
        else:
            analysis_path = f"us_market/macro_analysis_{'en' if lang == 'en' else ''}.json"

        if not os.path.exists(analysis_path):
            analysis_path = "us_market/macro_analysis.json"

        ai_analysis_default = "AI analysis not available. Run macro_analyzer.py."
        ai_analysis = ai_analysis_default

        if os.path.exists(analysis_path):
            with open(analysis_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                ai_analysis = cached.get("ai_analysis", ai_analysis_default)
                macro_indicators = cached.get("macro_indicators", {})

        # Fetch live indicator prices
        for name, ticker in {
            "VIX": "^VIX", "SPY": "SPY", "QQQ": "QQQ",
            "BTC": "BTC-USD", "GOLD": "GC=F",
        }.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty and len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change = current - prev
                    change_pct = (change / prev) * 100 if prev != 0 else 0
                    macro_indicators[name] = {
                        "current": round(current, 2),
                        "change_1d": round(change_pct, 2),
                    }
            except Exception:
                pass

        return jsonify({
            "macro_indicators": macro_indicators,
            "ai_analysis": ai_analysis,
            "model": model,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        logger.error("Error getting macro analysis", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/sector-heatmap")
def get_us_sector_heatmap():
    """Get sector heatmap data."""
    try:
        heatmap_path = "us_market/sector_heatmap.json"
        if not os.path.exists(heatmap_path):
            return jsonify({"error": "Sector heatmap data not found"}), 404

        with open(heatmap_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        logger.error("Error getting sector heatmap", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/options-flow")
def get_us_options_flow():
    """Get options flow data."""
    try:
        flow_path = "us_market/options_flow.json"
        if not os.path.exists(flow_path):
            return jsonify({"error": "Options flow data not found"}), 404

        with open(flow_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        logger.error("Error getting options flow", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/calendar")
def get_us_calendar():
    """Get weekly economic calendar."""
    try:
        calendar_path = "us_market/weekly_calendar.json"

        if not os.path.exists(calendar_path):
            return jsonify({
                "events": [],
                "message": "Calendar data not available. Run economic calendar generator first.",
            }), 404

        with open(calendar_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify(data)

    except Exception as e:
        logger.error("Error loading calendar data", error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/ai-summary/<ticker>")
def get_us_ai_summary(ticker):
    """Get AI-generated summary for a US stock."""
    try:
        lang = request.args.get("lang", "ko")
        if lang not in ["ko", "en"]:
            lang = "ko"

        summary_path = "us_market/ai_summaries.json"

        if not os.path.exists(summary_path):
            return jsonify({"error": "AI summaries not found. Run ai_summary_generator.py first."}), 404

        with open(summary_path, "r", encoding="utf-8") as f:
            summaries = json.load(f)

        if ticker not in summaries:
            return jsonify({"error": f"Summary not found for {ticker}"}), 404

        summary_data = summaries[ticker]

        if lang == "en":
            summary = summary_data.get("summary_en", summary_data.get("summary_ko", ""))
        else:
            summary = summary_data.get("summary_ko", summary_data.get("summary_en", ""))

        return jsonify({
            "ticker": ticker,
            "summary": summary,
            "lang": lang,
            "news_count": summary_data.get("news_count", 0),
            "updated": summary_data.get("updated", ""),
            "sentiment": summary_data.get("sentiment", "N/A"),
        })

    except Exception as e:
        logger.error("Error getting AI summary", ticker=ticker, error=str(e))
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/technical-indicators/<ticker>")
def get_technical_indicators(ticker):
    """Get technical indicators for a US stock."""
    try:
        import yfinance as yf
        import pandas as pd
        import numpy as np
        import traceback

        period = request.args.get("period", "1y")
        valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        if period not in valid_periods:
            period = "1y"

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return jsonify({"error": f"No data found for {ticker}"}), 404

        df = hist.copy()
        close = df["Close"]

        # Try to import TA library
        try:
            from ta.momentum import RSIIndicator
            from ta.trend import MACD
            from ta.volatility import BollingerBands
            TA_AVAILABLE = True
        except ImportError:
            TA_AVAILABLE = False

        # Calculate RSI
        if TA_AVAILABLE:
            rsi_indicator = RSIIndicator(close=close, window=14)
            rsi = rsi_indicator.rsi()
        else:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

        # Calculate MACD
        if TA_AVAILABLE:
            macd_obj = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
            macd_line = macd_obj.macd()
            signal_line = macd_obj.macd_signal()
            macd_histogram = macd_obj.macd_diff()
        else:
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_histogram = macd_line - signal_line

        # Calculate Bollinger Bands
        if TA_AVAILABLE:
            bb = BollingerBands(close=close, window=20, window_dev=2)
            bb_upper = bb.bollinger_hband()
            bb_middle = bb.bollinger_mavg()
            bb_lower = bb.bollinger_lband()
        else:
            bb_middle = close.rolling(window=20).mean()
            std = close.rolling(window=20).std()
            bb_upper = bb_middle + (std * 2)
            bb_lower = bb_middle - (std * 2)

        # Support and Resistance
        def detect_support_resistance(df, window=10):
            supports = []
            resistances = []
            high = df["High"].values
            low = df["Low"].values

            for i in range(window, len(df) - window):
                if low[i] == np.min(low[i - window : i + window + 1]):
                    supports.append(float(low[i]))
                if high[i] == np.max(high[i - window : i + window + 1]):
                    resistances.append(float(high[i]))

            def cluster_levels(levels):
                if not levels:
                    return []
                levels = sorted(levels)
                clusters = []
                current_cluster = [levels[0]]
                for level in levels[1:]:
                    if (level - current_cluster[0]) / current_cluster[0] <= 0.02:
                        current_cluster.append(level)
                    else:
                        clusters.append(sum(current_cluster) / len(current_cluster))
                        current_cluster = [level]
                if current_cluster:
                    clusters.append(sum(current_cluster) / len(current_cluster))
                return [round(c, 2) for c in clusters[-5:]]

            return cluster_levels(supports), cluster_levels(resistances)

        supports, resistances = detect_support_resistance(df)

        def make_series(dates, values):
            result = []
            for date, val in zip(dates, values):
                if pd.notna(val):
                    result.append({"time": int(date.timestamp()), "value": round(float(val), 2)})
            return result

        response = {
            "ticker": ticker,
            "period": period,
            "rsi": make_series(df.index, rsi),
            "macd": {
                "macd_line": make_series(df.index, macd_line),
                "signal_line": make_series(df.index, signal_line),
                "histogram": make_series(df.index, macd_histogram),
            },
            "bollinger": {
                "upper": make_series(df.index, bb_upper),
                "middle": make_series(df.index, bb_middle),
                "lower": make_series(df.index, bb_lower),
            },
            "support_resistance": {"support": supports, "resistance": resistances},
        }

        return jsonify(response)

    except Exception as e:
        logger.error("Error getting technical indicators", ticker=ticker, error=str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@market_bp.route("/api/us/update-data", methods=["POST"])
def update_market_data():
    """Trigger market data update."""
    try:
        import subprocess

        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "us_market", "update_all.py")

        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Update script not found"}), 404

        subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )

        return jsonify({
            "success": True,
            "message": "Data update started in background. This may take 30-40 minutes to complete.",
            "note": "For faster updates, please use GitHub Actions or run scripts locally.",
            "status": "started",
            "script": script_path
        })

    except Exception as e:
        logger.error("Error starting data update", error=str(e))
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
