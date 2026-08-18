import asyncio
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Query
from app.services.location_service import get_coordinates
from app.services.weather_service import (
    get_current_weather,
    get_weather_15_days
)
from app.services.weather_analyzer import WeatherAnalyzer
from app.services.extreme_weather import ExtremeWeatherAnalyzer
from app.services.air_quality_service import AirQualityService
from app.services.agriculture_service import AgricultureService
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import (
    AirQualityResponse,
    LifestyleRecommendationResponse,
    AgricultureRecommendationResponse,
    OverviewRecommendationResponse
)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Smart Recommendations & Intelligence"]
)


@router.get("/air-quality", response_model=AirQualityResponse)
async def get_air_quality_analysis(city: str = Query(..., description="Tên thành phố (ví dụ: Ha Noi, Ho Chi Minh, Da Nang)")):
    """
    BE 3 - Trụ cột 3: Phân tích chất lượng không khí (AQI).
    Lấy dữ liệu PM2.5, PM10, CO, NO2, O3, SO2 từ Open-Meteo Air Quality API,
    tính chỉ số AQI tổng hợp, phân loại mức độ ô nhiễm và đưa ra khuyến nghị y tế.
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        raw_aq_data = await AirQualityService.fetch_air_quality(location["lat"], location["lon"])
        aq_analysis = AirQualityService.analyze_air_quality(raw_aq_data)

        return {
            "success": True,
            "location": location,
            "air_quality": aq_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifestyle", response_model=LifestyleRecommendationResponse)
async def get_lifestyle_recommendations(city: str = Query(..., description="Tên thành phố")):
    """
    BE 3 - Trụ cột 2: Gợi ý sinh hoạt đời sống thông minh.
    Dựa vào nhiệt độ, cảm giác nhiệt, xác suất mưa, gió, mã thời tiết và AQI để gợi ý:
    Trang phục, tính khả thi các hoạt động ngoài trời, an toàn sức khỏe và giao thông.
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        lat, lon = location["lat"], location["lon"]

        # Gọi đồng thời thời tiết hiện tại, 15 ngày và chất lượng không khí
        weather_curr_task = get_current_weather(lat, lon)
        weather_15d_task = get_weather_15_days(lat, lon)
        aq_task = AirQualityService.fetch_air_quality(lat, lon)

        curr_res, days_res, aq_res = await asyncio.gather(
            weather_curr_task,
            weather_15d_task,
            aq_task,
            return_exceptions=True
        )

        current_data = {}
        if not isinstance(curr_res, Exception):
            raw_curr = curr_res.get("current", {})
            current_data = {
                "temperature": raw_curr.get("temperature_2m"),
                "feels_like": raw_curr.get("apparent_temperature"),
                "humidity": raw_curr.get("relative_humidity_2m"),
                "precipitation": raw_curr.get("precipitation"),
                "wind_speed": raw_curr.get("wind_speed_10m"),
                "weather_code": raw_curr.get("weather_code")
            }

        daily_data = {}
        if not isinstance(days_res, Exception):
            daily = days_res.get("daily", {})
            if "precipitation_probability_max" in daily and len(daily["precipitation_probability_max"]) > 7:
                daily_data = {
                    "rain_probability": daily["precipitation_probability_max"][7], # Hôm nay
                    "precipitation": daily["precipitation_sum"][7] if "precipitation_sum" in daily else 0.0
                }

        aq_analysis = {}
        if not isinstance(aq_res, Exception):
            aq_analysis = AirQualityService.analyze_air_quality(aq_res)

        lifestyle_rec = RecommendationService.generate_lifestyle_recommendation(
            current_weather=current_data,
            daily_weather=daily_data,
            air_quality=aq_analysis
        )

        return {
            "success": True,
            "location": location,
            "lifestyle_recommendations": lifestyle_rec
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agriculture", response_model=AgricultureRecommendationResponse)
async def get_agriculture_recommendations(city: str = Query(..., description="Tên thành phố")):
    """
    BE 3 - Trụ cột 1: Nông nghiệp thông minh (Smart Agriculture).
    Phân tích nhiệt độ, lượng mưa, độ ẩm, mùa vụ và vùng sinh thái thổ nhưỡng.
    Sử dụng kết hợp Rule-Based Agronomy Engine và Machine Learning Random Forest
    để đề xuất cây trồng tối ưu, kế hoạch tưới tiêu và cảnh báo sâu bệnh / thời tiết cực đoan.
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        lat, lon = location["lat"], location["lon"]
        weather_15d = await get_weather_15_days(lat, lon)
        daily = weather_15d.get("daily", {})

        if not daily or len(daily.get("time", [])) < 15:
            raise HTTPException(status_code=500, detail="Không đủ dữ liệu thời tiết để phân tích nông nghiệp.")

        weather_analysis = WeatherAnalyzer.analyze_daily_data(daily)

        agri_rec = AgricultureService.recommend_crops(
            lat=lat,
            lon=lon,
            city_name=location["name"],
            weather_analysis=weather_analysis
        )

        return {
            "success": True,
            "location": location,
            "agriculture_recommendations": agri_rec
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview", response_model=OverviewRecommendationResponse)
async def get_overview_intelligence(city: str = Query(..., description="Tên thành phố")):
    """
    BE 3: Tổng hợp toàn diện phân tích thông minh và khuyến nghị:
    - Thời tiết hiện tại & 15 ngày
    - Chất lượng không khí (AQI)
    - Cảnh báo hiện tượng cực đoan & bất thường
    - Gợi ý sinh hoạt (Trang phục, ngoài trời, sức khỏe, giao thông)
    - Nông nghiệp thông minh (Đề xuất cây trồng Rule-Based + Machine Learning)
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        lat, lon = location["lat"], location["lon"]

        # Gọi đồng thời cả 3 nguồn API
        curr_res, days_res, aq_res = await asyncio.gather(
            get_current_weather(lat, lon),
            get_weather_15_days(lat, lon),
            AirQualityService.fetch_air_quality(lat, lon),
            return_exceptions=True
        )

        current_data = {}
        if not isinstance(curr_res, Exception):
            raw_curr = curr_res.get("current", {})
            current_data = {
                "temperature": raw_curr.get("temperature_2m"),
                "feels_like": raw_curr.get("apparent_temperature"),
                "humidity": raw_curr.get("relative_humidity_2m"),
                "precipitation": raw_curr.get("precipitation"),
                "wind_speed": raw_curr.get("wind_speed_10m"),
                "weather_code": raw_curr.get("weather_code")
            }

        daily = {}
        weather_analysis = {}
        extremes_result = {}
        daily_today = {}
        if not isinstance(days_res, Exception):
            daily = days_res.get("daily", {})
            if daily and len(daily.get("time", [])) >= 15:
                history_daily = {k: v[:7] for k, v in daily.items() if isinstance(v, list)}
                weather_analysis = WeatherAnalyzer.analyze_daily_data(daily)
                extremes_result = ExtremeWeatherAnalyzer.analyze_extremes(daily, historical_baseline=history_daily)
                daily_today = {
                    "rain_probability": daily.get("precipitation_probability_max", [0]*15)[7],
                    "precipitation": daily.get("precipitation_sum", [0]*15)[7]
                }

        aq_analysis = {}
        if not isinstance(aq_res, Exception):
            aq_analysis = AirQualityService.analyze_air_quality(aq_res)

        lifestyle_rec = RecommendationService.generate_lifestyle_recommendation(
            current_weather=current_data,
            daily_weather=daily_today,
            air_quality=aq_analysis
        )

        agri_rec = AgricultureService.recommend_crops(
            lat=lat,
            lon=lon,
            city_name=location["name"],
            weather_analysis=weather_analysis
        )

        return {
            "success": True,
            "location": location,
            "current_weather": current_data,
            "air_quality": aq_analysis,
            "extreme_alerts": extremes_result,
            "lifestyle_recommendations": lifestyle_rec,
            "agriculture_recommendations": agri_rec
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
