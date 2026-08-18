from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from app.schemas.weather import LocationSchema


class WeatherAlertItem(BaseModel):
    date: str
    type: str
    level: str
    message: str
    advice: Optional[str] = None


class ExtremeWeatherResponse(BaseModel):
    success: bool
    location: LocationSchema
    overall_severity: str
    total_alerts: int
    summary: str
    alerts: List[WeatherAlertItem]
    historical_comparison: Optional[Dict[str, Any]] = None


class WeatherAnalysisSummaryResponse(BaseModel):
    success: bool
    location: LocationSchema
    period: Dict[str, Any]
    analysis: Dict[str, Any]
    comparison_trend: Optional[Dict[str, Any]] = None
