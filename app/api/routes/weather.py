from fastapi import APIRouter, HTTPException

from app.services.location_service import get_coordinates
from app.services.weather_service import (
    get_current_weather,
    get_weather_history,
    get_weather_forecast)


router = APIRouter(
    prefix="/api/weather",
    tags=["Weather"]
)


@router.get("/current")
async def current_weather(city: str):

    try:
        location = await get_coordinates(city)

        if not location:

            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )

        lat = location["lat"]
        lon = location["lon"]


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
# 7 DAYS HISTORY
# ==========================================

@router.get("/history")
async def weather_history(city: str):

    try:

        location = await get_coordinates(city)

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )

        weather = await get_weather_history(
            location["lat"],
            location["lon"]
        )

        return {
            "success": True,

            "location": {
                "name": location["name"],
                "country": location["country"],
                "state": location.get("state"),
                "lat": location["lat"],
                "lon": location["lon"],
                "timezone": location.get("timezone")
            },

            "period": {
                "type": "history",
                "days": 7
            },

            "daily": weather.get("daily")
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
# 7 DAYS FORECAST
# ==========================================

@router.get("/forecast")
async def weather_forecast(city: str):

    try:

        location = await get_coordinates(city)

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thành phố: {city}"
            )

        weather = await get_weather_forecast(
            location["lat"],
            location["lon"]
        )

        return {
            "success": True,

            "location": {
                "name": location["name"],
                "country": location["country"],
                "state": location.get("state"),
                "lat": location["lat"],
                "lon": location["lon"],
                "timezone": location.get("timezone")
            },

            "period": {
                "type": "forecast",
                "days": 7
            },

            "daily": weather.get("daily")
        }

    except HTTPException:
        raise

    except Exception as e:

        print("ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )