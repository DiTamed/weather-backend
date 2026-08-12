from fastapi import APIRouter, HTTPException

from app.services.location_service import get_coordinates

from app.services.weather_service import (
    get_current_weather,
    get_weather_15_days
)
# Import module phân tích của Vinh
from app.services.weather_analyzer import WeatherAnalyzer
# Import module cảnh báo của Thắng
from app.services.extreme_weather import ExtremeWeatherAnalyzer

router = APIRouter(
    prefix="/api/weather",
    tags=["Weather"]
)

# ==========================================
# CURRENT WEATHER
# ==========================================

@router.get("/current")
async def current_weather(city: str):

    try:

        # Tìm thành phố
        location = await get_coordinates(city)

        if not location:

            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )

        lat = location["lat"]
        lon = location["lon"]


        # Lấy thời tiết hiện tại
        weather = await get_current_weather(
            lat,
            lon
        )

        current = weather["current"]


        return {

            "success": True,

            "location": {

                "name": location["name"],

                "country": location["country"],

                "state": location.get("state"),

                "lat": lat,

                "lon": lon,

                "timezone": location.get("timezone")

            },

            "current": {

                "temperature": current.get(
                    "temperature_2m"
                ),

                "feels_like": current.get(
                    "apparent_temperature"
                ),

                "humidity": current.get(
                    "relative_humidity_2m"
                ),

                "precipitation": current.get(
                    "precipitation"
                ),

                "wind_speed": current.get(
                    "wind_speed_10m"
                ),

                "weather_code": current.get(
                    "weather_code"
                )

            }

        }


    except HTTPException:

        raise


    except Exception as e:

        print("ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# 15 DAYS WEATHER (CÓ THÊM PHÂN TÍCH)
# 7 DAYS BEFORE + TODAY + 7 DAYS AFTER
# ==========================================

@router.get("/15-days")
async def weather_15_days(city: str):
    try:
        # =====================================
        # 1. Lấy latitude / longitude
        # =====================================
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )
        lat = location["lat"]
        lon = location["lon"]

        # =====================================
        # 2. Lấy dữ liệu Open-Meteo
        # =====================================
        weather = await get_weather_15_days(lat, lon)
        daily = weather.get("daily", {})
        dates = daily.get("time", [])
        result = []

        # =====================================
        # 3. Chạy logic phân tích Pandas của Vinh
        # =====================================
        analysis_result = {}
        comparison_result = {}
        
        if daily and len(dates) >= 15:
            # Tách data thành 2 mảng: 7 ngày trước và 7 ngày sau (bỏ qua ngày hiện tại ở giữa)
            history_daily = {key: val[:7] for key, val in daily.items() if isinstance(val, list)}
            forecast_daily = {key: val[8:15] for key, val in daily.items() if isinstance(val, list)}
            
            # Gọi 2 hàm trong weather_analyzer.py
            analysis_result = WeatherAnalyzer.analyze_daily_data(daily)
            comparison_result = WeatherAnalyzer.compare_history_vs_forecast(history_daily, forecast_daily)

        # =====================================
        # 4. Convert dữ liệu danh sách ngày
        # =====================================
        for i, date in enumerate(dates):
            result.append({
                "date": date,
                "temperature": {
                    "max": daily["temperature_2m_max"][i],
                    "min": daily["temperature_2m_min"][i]
                },
                "feels_like": {
                    "max": daily["apparent_temperature_max"][i],
                    "min": daily["apparent_temperature_min"][i]
                },
                "humidity": daily["relative_humidity_2m_mean"][i],
                "precipitation": daily["precipitation_sum"][i],
                "rain": daily["rain_sum"][i],
                "rain_probability": daily["precipitation_probability_max"][i],
                "wind_speed": daily["wind_speed_10m_max"][i],
                "weather_code": daily["weather_code"][i]
            })

        # =====================================
        # 5. Response
        # =====================================
        return {
            "success": True,
            "location": {
                "name": location["name"],
                "country": location["country"],
                "state": location.get("state"),
                "lat": lat,
                "lon": lon,
                "timezone": location.get("timezone")
            },
            "period": {
                "past_days": 7,
                "today": 1,
                "future_days": 7,
                "total_days": len(result)
            },
            # Trả thêm 2 block kết quả phân tích
            "analysis": analysis_result,
            "comparison_trend": comparison_result,
            
            "daily": result
        }

    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)

        )

# ==========================================
# BE 2: CẢNH BÁO THỜI TIẾT BẤT THƯỜNG
# ==========================================
@router.get("/alerts")
async def weather_alerts(city: str):
    try:
        location = await get_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thành phố: {city}")

        weather = await get_weather_15_days(location["lat"], location["lon"])
        daily = weather.get("daily", {})

        if not daily or "time" not in daily or len(daily["time"]) < 15:
            return {"success": False, "message": "Không đủ dữ liệu thời tiết"}

        # Cắt 7 ngày đầu tiên làm dữ liệu lịch sử (baseline)
        history_daily = {key: val[:7] for key, val in daily.items() if isinstance(val, list)}

        # Đưa toàn bộ data và history vào phân tích
        alerts_result = ExtremeWeatherAnalyzer.analyze_extremes(daily, historical_baseline=history_daily)

        return {
            "success": True,
            "location": {
                "name": location["name"],
                "country": location["country"]
            },
            "alerts_data": alerts_result
        }

    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

        
