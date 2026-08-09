from fastapi import APIRouter, HTTPException

from app.services.location_service import get_coordinates
from app.services.weather_service import get_current_weather


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

        return {

    "success": True,

    "location": {
        "name": location["name"],
        "country": location["country"],
        "lat": lat,
        "lon": lon
    },

    "current": {

        "temperature": weather["main"]["temp"],

        "feels_like": weather["main"]["feels_like"],

        "humidity": weather["main"]["humidity"],

        "pressure": weather["main"]["pressure"],

        "wind_speed": weather["wind"]["speed"],

        "weather": weather["weather"][0]["main"],

        "description": weather["weather"][0]["description"]

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