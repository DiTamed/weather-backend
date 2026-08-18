from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    name: str
    lat: float
    lon: float
    country: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = None


class CurrentWeatherDetail(BaseModel):
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_code: Optional[int] = None


class CurrentWeatherResponse(BaseModel):
    success: bool
    location: LocationSchema
    current: CurrentWeatherDetail


class DailyWeatherItem(BaseModel):
    date: str
    temperature: Dict[str, Optional[float]]
    feels_like: Dict[str, Optional[float]]
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    rain: Optional[float] = None
    rain_probability: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_code: Optional[int] = None


class PeriodSchema(BaseModel):
    past_days: int
    today: int
    future_days: int
    total_days: int


class Weather15DaysResponse(BaseModel):
    success: bool
    location: LocationSchema
    period: PeriodSchema
    analysis: Optional[Dict[str, Any]] = None
    comparison_trend: Optional[Dict[str, Any]] = None
    daily: List[DailyWeatherItem]
