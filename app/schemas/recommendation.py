from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from app.schemas.weather import LocationSchema


class AirQualityResponse(BaseModel):
    success: bool
    location: LocationSchema
    air_quality: Dict[str, Any]


class LifestyleRecommendationResponse(BaseModel):
    success: bool
    location: LocationSchema
    lifestyle_recommendations: Dict[str, Any]


class AgricultureRecommendationResponse(BaseModel):
    success: bool
    location: LocationSchema
    agriculture_recommendations: Dict[str, Any]


class OverviewRecommendationResponse(BaseModel):
    success: bool
    location: LocationSchema
    current_weather: Dict[str, Any]
    air_quality: Dict[str, Any]
    extreme_alerts: Dict[str, Any]
    lifestyle_recommendations: Dict[str, Any]
    agriculture_recommendations: Dict[str, Any]
