# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import weather, analysis, recommendation

app = FastAPI(
    title="Weather Analysis & Intelligent Recommendation API",
    description="Hệ thống Backend FastAPI phân tích dữ liệu thời tiết, phát hiện bất thường & cảnh báo, và phân tích thông minh & đề xuất",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router chính
app.include_router(weather.router)
app.include_router(analysis.router)
app.include_router(recommendation.router)


@app.get("/")
async def root():
    return {
        "message": "Weather Analysis & Intelligent Recommendation API is running",
        "version": "2.0.0",
        "docs_url": "/docs",
        "modules": {
           "Analysis": "Phân tích dữ liệu thời tiết, phát hiện bất thường & cảnh báo",
           "Recommendation": "Phân tích thông minh"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "weather-backend"
    }