import httpx
from app.config import OPENWEATHER_API_KEY, OPENWEATHER_GEO_URL

async def get_coordinates(city: str):
    url = f"{OPENWEATHER_GEO_URL}/direct"

    params = {
        "q": city,
        "limit": 11,
        "appid": OPENWEATHER_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None

        location = data[0]

        return {
            "name": location.get("name"),
            "lat": location.get("lat"),
            "lon": location.get("lon"),
            "country": location.get("country"),
            "state": location.get("state")
        }