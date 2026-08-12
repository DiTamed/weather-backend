from fastapi import APIRouter, HTTPException

from app.services.location_service import get_coordinates

from app.services.weather_service import (
    get_current_weather,
    get_weather_15_days
)


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
# 15 DAYS WEATHER
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

        weather = await get_weather_15_days(
            lat,
            lon
        )


        daily = weather.get(
            "daily",
            {}
        )


        # =====================================
        # 3. Lấy danh sách ngày
        # =====================================

        dates = daily.get(
            "time",
            []
        )


        result = []


        # =====================================
        # 4. Convert dữ liệu
        # =====================================

        for i, date in enumerate(dates):

            result.append({

                "date": date,

                "temperature": {

                    "max": daily[
                        "temperature_2m_max"
                    ][i],

                    "min": daily[
                        "temperature_2m_min"
                    ][i]

                },

                "feels_like": {

                    "max": daily[
                        "apparent_temperature_max"
                    ][i],

                    "min": daily[
                        "apparent_temperature_min"
                    ][i]

                },

                "humidity": daily[
                    "relative_humidity_2m_mean"
                ][i],

                "precipitation": daily[
                    "precipitation_sum"
                ][i],

                "rain": daily[
                    "rain_sum"
                ][i],

                "rain_probability": daily[
                    "precipitation_probability_max"
                ][i],

                "wind_speed": daily[
                    "wind_speed_10m_max"
                ][i],

                "weather_code": daily[
                    "weather_code"
                ][i]

            })


        # =====================================
        # 5. Response
        # =====================================

        return {

            "success": True,

            "location": {

                "name": location["name"],

                "country": location["country"],

                "state": location.get(
                    "state"
                ),

                "lat": lat,

                "lon": lon,

                "timezone": location.get(
                    "timezone"
                )

            },

            "period": {

                "past_days": 7,

                "today": 1,

                "future_days": 7,

                "total_days": len(result)

            },

            "daily": result

        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )