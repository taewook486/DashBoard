"""
Input validation utilities using Pydantic models.
@SPEC:IMPROVE-001 REQ-SEC-002
"""

import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class ChartPeriod(str, Enum):
    """Valid chart periods."""
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    MAX = "max"


class Language(str, Enum):
    """Supported languages."""
    KOREAN = "ko"
    ENGLISH = "en"


class AIModel(str, Enum):
    """Supported AI models."""
    GEMINI = "gemini"
    GPT = "gpt"


# Ticker symbol pattern (letters, numbers, hyphens, dots, carets)
TICKER_PATTERN = re.compile(r'^[A-Z0-9.\-^]{1,10}$')


class TickerValidator(BaseModel):
    """Validator for ticker symbols."""
    ticker: str = Field(..., min_length=1, max_length=10,
                       description="Stock ticker symbol")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate ticker format."""
        v = v.upper().strip()

        if not TICKER_PATTERN.match(v):
            raise ValueError(
                f"Invalid ticker symbol: '{v}'. "
                "Ticker must contain only letters, numbers, hyphens, dots, or carets."
            )

        return v


class ChartRequest(BaseModel):
    """Request model for chart data."""
    ticker: str = Field(..., min_length=1, max_length=10)
    period: ChartPeriod = Field(default=ChartPeriod.ONE_YEAR)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate ticker format."""
        v = v.upper().strip()
        if not TICKER_PATTERN.match(v):
            raise ValueError(f"Invalid ticker symbol: '{v}'")
        return v


class AISummaryRequest(BaseModel):
    """Request model for AI summary."""
    ticker: str = Field(..., min_length=1, max_length=10)
    lang: Language = Field(default=Language.KOREAN)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate ticker format."""
        v = v.upper().strip()
        if not TICKER_PATTERN.match(v):
            raise ValueError(f"Invalid ticker symbol: '{v}'")
        return v


class MacroAnalysisRequest(BaseModel):
    """Request model for macro analysis."""
    lang: Language = Field(default=Language.KOREAN)
    model: AIModel = Field(default=AIModel.GEMINI)


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a ticker symbol.

    Args:
        ticker: Raw ticker string

    Returns:
        Normalized ticker (uppercase, stripped)

    Raises:
        ValidationError: If ticker is invalid
    """
    from app.utils.errors import ValidationError

    try:
        validated = TickerValidator(ticker=ticker)
        return validated.ticker
    except Exception as e:
        raise ValidationError(
            message=str(e),
            field='ticker',
            value=ticker,
            constraint='Must be a valid stock ticker (1-10 alphanumeric characters)'
        )


def validate_period(period: str) -> str:
    """
    Validate chart period parameter.

    Args:
        period: Period string

    Returns:
        Validated period or default '1y'
    """
    valid_periods = [p.value for p in ChartPeriod]
    if period in valid_periods:
        return period
    return '1y'  # Default fallback
