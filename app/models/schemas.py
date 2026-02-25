"""
Pydantic schemas for API validation and serialization.
@SPEC:IMPROVE-001 REQ-SEC-002
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import re

T = TypeVar('T')


# Enums
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


# Ticker validation pattern
TICKER_PATTERN = re.compile(r'^[A-Z0-9.\-^]{1,10}$')


# Request Models
class TickerRequest(BaseModel):
    """Request model for ticker-based endpoints."""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate and normalize ticker format."""
        v = v.upper().strip()
        if not TICKER_PATTERN.match(v):
            raise ValueError(
                f"Invalid ticker symbol: '{v}'. "
                "Must contain only letters, numbers, hyphens, dots, or carets (1-10 chars)."
            )
        return v


class ChartRequest(BaseModel):
    """Request model for chart data."""
    ticker: str = Field(..., min_length=1, max_length=10)
    period: ChartPeriod = Field(default=ChartPeriod.ONE_YEAR)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate and normalize ticker format."""
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
        """Validate and normalize ticker format."""
        v = v.upper().strip()
        if not TICKER_PATTERN.match(v):
            raise ValueError(f"Invalid ticker symbol: '{v}'")
        return v


class MacroAnalysisRequest(BaseModel):
    """Request model for macro analysis."""
    lang: Language = Field(default=Language.KOREAN)
    model: AIModel = Field(default=AIModel.GEMINI)


# Response Models
class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(default=False)
    error: ErrorDetail
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response."""
    success: bool = Field(default=True)
    data: Optional[T] = Field(default=None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Metadata")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")


# Candle data for charts
class CandleData(BaseModel):
    """Candlestick chart data."""
    time: int = Field(..., description="Unix timestamp")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Closing price")


# Index data
class IndexData(BaseModel):
    """Market index data."""
    name: str = Field(..., description="Index name")
    symbol: str = Field(..., description="Index symbol")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Percentage change")


class IndicesResponse(BaseModel):
    """Response for indices endpoint."""
    indices: List[IndexData]
