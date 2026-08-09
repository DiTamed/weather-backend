import httpx

from app.config import OPEN_METEO_GEO_URL


async def get_coordinates(city: str):

    params = {
        "name": city,
        "count": 1,
        "language": "vi",
        "format": "json"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:

        response = await client.get(
            OPEN_METEO_GEO_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    results = data.get("results", [])

    if not results:
        return None

    location = results[0]

    return {
        "name": location.get("name"),
        "lat": location.get("latitude"),
        "lon": location.get("longitude"),
        "country": location.get("country"),
        "state": location.get("admin1"),
        "timezone": location.get("timezone")
    }