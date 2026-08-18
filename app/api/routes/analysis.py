# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Query
from app.services.location_service import get_coordinates
from app.services.weather_service import get_weather_15_days
from app.services.weather_analyzer import WeatherAnalyzer
from app.services.extreme_weather import ExtremeWeatherAnalyzer
from app.schemas.analysis import (
    WeatherAnalysisSummaryResponse,
    ExtremeWeatherResponse
)

router = APIRouter(
    prefix="/api/analysis",
    tags=["Weather Analysis & Extremes"]
)


@router.get("/summary", response_model=WeatherAnalysisSummaryResponse)
async def get_weather_analysis_summary(city: str = Query(..., description="Tên thành phố (ví dụ: Ho Chi Minh, Ha Noi, Da Nang)")):
    """
    BE 1: Phân tích dữ liệu thời tiết thống kê (Nhiệt độ, Lượng mưa, Độ ẩm, Gió, Cảm giác nhiệt)
    dựa trên chu kỳ 15 ngày (7 ngày lịch sử + hôm nay + 7 ngày dự báo).
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        weather = await get_weather_15_days(location["lat"], location["lon"])
        daily = weather.get("daily", {})
        dates = daily.get("time", [])

        if not daily or len(dates) < 15:
            raise HTTPException(status_code=500, detail="Không đủ dữ liệu thời tiết từ Open-Meteo để phân tích.")

        history_daily = {k: v[:7] for k, v in daily.items() if isinstance(v, list)}
        forecast_daily = {k: v[8:15] for k, v in daily.items() if isinstance(v, list)}

        analysis_result = WeatherAnalyzer.analyze_daily_data(daily)
        comparison_result = WeatherAnalyzer.compare_history_vs_forecast(history_daily, forecast_daily)

        return {
            "success": True,
            "location": location,
            "period": {
                "past_days": 7,
                "today": 1,
                "future_days": 7,
                "total_days": len(dates)
            },
            "analysis": analysis_result,
            "comparison_trend": comparison_result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_weather_trends(city: str = Query(..., description="Tên thành phố")):
    """
    BE 1: So sánh dữ liệu 7 ngày quá khứ và 7 ngày tương lai để phát hiện xu hướng biến đổi thời tiết.
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        weather = await get_weather_15_days(location["lat"], location["lon"])
        daily = weather.get("daily", {})

        if not daily or len(daily.get("time", [])) < 15:
            raise HTTPException(status_code=500, detail="Không đủ dữ liệu thời tiết để phân tích xu hướng.")

        history_daily = {k: v[:7] for k, v in daily.items() if isinstance(v, list)}
        forecast_daily = {k: v[8:15] for k, v in daily.items() if isinstance(v, list)}

        comparison = WeatherAnalyzer.compare_history_vs_forecast(history_daily, forecast_daily)

        return {
            "success": True,
            "location": location,
            "trend_comparison": comparison
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/extremes", response_model=ExtremeWeatherResponse)
async def get_extreme_weather_alerts(city: str = Query(..., description="Tên thành phố")):
    """
    BE 2: Phát hiện các hiện tượng thời tiết bất thường, cực đoan (nắng nóng gay gắt, đợt nắng nóng kéo dài,
    rét đậm rét hại, mưa lớn ngập lụt, bão gió mạnh, độ ẩm bất thường) và phân cấp cảnh báo.
    """
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        weather = await get_weather_15_days(location["lat"], location["lon"])
        daily = weather.get("daily", {})

        if not daily or len(daily.get("time", [])) < 15:
            raise HTTPException(status_code=500, detail="Không đủ dữ liệu thời tiết để phân tích cảnh báo.")

        history_daily = {k: v[:7] for k, v in daily.items() if isinstance(v, list)}
        extremes_result = ExtremeWeatherAnalyzer.analyze_extremes(daily, historical_baseline=history_daily)

        return {
            "success": True,
            "location": location,
            "overall_severity": extremes_result["overall_severity"],
            "total_alerts": extremes_result["total_alerts"],
            "summary": extremes_result["summary"],
            "alerts": extremes_result["alerts"],
            "historical_comparison": extremes_result["historical_comparison"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
