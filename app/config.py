import os
from dotenv import load_dotenv

load_dotenv()

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL")
OPEN_METEO_GEO_URL = os.getenv("OPEN_METEO_GEO_URL")