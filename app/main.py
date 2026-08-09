from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import weather
app = FastAPI(
    title="Weather Analysis API",
    description="API phân tích và dự báo thời tiết",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
@app.get("/")
async def root():
     return {
        "message": "Weather Analysis API is running"
    }
@app.get("/health")
def health():
    return {
        "status": "ok"
    }