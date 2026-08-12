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


# =========================================================
# CURRENT WEATHER
# =========================================================

@router.get("/current")
async def current_weather(city: str):

    try:

        # 1. Tìm thành phố
        location = await get_coordinates(city)

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )

        lat = location["lat"]
        lon = location["lon"]


        # 2. Lấy thời tiết hiện tại
        weather = await get_current_weather(
            lat,
            lon
        )

        current = weather.get("current", {})


        return {

            "success": True,

            "location": {

                "name": location.get("name"),

                "country": location.get("country"),

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

        print(
            "CURRENT WEATHER ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể lấy dữ liệu thời tiết hiện tại."
        )


# =========================================================
# 15 DAYS WEATHER
#
# 7 ngày trước
# + hôm nay
# + 7 ngày sau
# =========================================================

@router.get("/15-days")
async def weather_15_days(city: str):

    try:

        # =================================================
        # 1. Lấy tọa độ thành phố
        # =================================================

        location = await get_coordinates(city)

        if not location:

            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )


        lat = location["lat"]
        lon = location["lon"]


        # =================================================
        # 2. Lấy dữ liệu từ Open-Meteo
        # =================================================

        weather = await get_weather_15_days(
            lat,
            lon
        )


        daily = weather.get(
            "daily",
            {}
        )


        # =================================================
        # 3. Kiểm tra dữ liệu
        # =================================================

        dates = daily.get(
            "time",
            []
        )

        if not dates:

            raise HTTPException(
                status_code=404,
                detail="Không có dữ liệu thời tiết."
            )


        # =================================================
        # 4. Convert dữ liệu
        # =================================================

        result = []


        for i, date in enumerate(dates):

            result.append({

                "date": date,

                # -----------------------------------------
                # Temperature
                # -----------------------------------------

                "temperature": {

                    "max": daily[
                        "temperature_2m_max"
                    ][i],

                    "min": daily[
                        "temperature_2m_min"
                    ][i]

                },

                # -----------------------------------------
                # Feels Like
                # -----------------------------------------

                "feels_like": {

                    "max": daily[
                        "apparent_temperature_max"
                    ][i],

                    "min": daily[
                        "apparent_temperature_min"
                    ][i]

                },

                # -----------------------------------------
                # Humidity
                # -----------------------------------------

                "humidity": daily[
                    "relative_humidity_2m_mean"
                ][i],

                # -----------------------------------------
                # Rain
                # -----------------------------------------

                "precipitation": daily[
                    "precipitation_sum"
                ][i],

                "rain": daily[
                    "rain_sum"
                ][i],

                "rain_probability": daily[
                    "precipitation_probability_max"
                ][i],

                # -----------------------------------------
                # Wind
                # -----------------------------------------

                "wind_speed": daily[
                    "wind_speed_10m_max"
                ][i],

                # -----------------------------------------
                # Weather Code
                # -----------------------------------------

                "weather_code": daily[
                    "weather_code"
                ][i]

            })


        # =================================================
        # 5. Response
        # =================================================

        return {

            "success": True,

            "location": {

                "name": location.get(
                    "name"
                ),

                "country": location.get(
                    "country"
                ),

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
            "15 DAYS WEATHER ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail="Không thể lấy dữ liệu thời tiết 15 ngày."

        )