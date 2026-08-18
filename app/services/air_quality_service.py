import asyncio
from typing import Dict, Any, Optional
# pyrefly: ignore [missing-import]
import httpx
from app.config import OPEN_METEO_AIR_QUALITY_URL
from app.utils.calculations import (
    calculate_aqi_subindex,
    get_aqi_level_details,
    clean_numpy_types
)


class AirQualityService:
    """
    BE 3 - Trụ cột 3: Phân tích chất lượng không khí (AQI).
    Lấy dữ liệu nồng độ bụi mịn PM2.5, PM10, CO, NO2, O3, SO2 từ Open-Meteo Air Quality API
    và tính toán chỉ số AQI, mức độ ô nhiễm, chất gây ô nhiễm chính và khuyến nghị sức khỏe.
    """

    @staticmethod
    async def fetch_air_quality(lat: float, lon: float) -> Dict[str, Any]:
        """
        Gọi Open-Meteo Air Quality API để lấy nồng độ chất ô nhiễm hiện tại và dự báo.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join([
                "pm10",
                "pm2_5",
                "carbon_monoxide",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone",
                "us_aqi",
                "european_aqi"
            ]),
            "hourly": ",".join([
                "pm10",
                "pm2_5",
                "us_aqi"
            ]),
            "forecast_days": 2,
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(
                        OPEN_METEO_AIR_QUALITY_URL,
                        params=params
                    )
                    if response.status_code == 429:
                        if attempt < 2:
                            await asyncio.sleep(5)
                            continue
                        raise Exception("Open-Meteo Air Quality API rate limited (429).")
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if attempt == 2:
                        raise e
                except Exception as e:
                    if attempt == 2:
                        raise e
            raise Exception("Không thể kết nối đến Open-Meteo Air Quality API.")

    @staticmethod
    def analyze_air_quality(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý dữ liệu thô ô nhiễm không khí, tính toán chỉ số AQI và đưa ra khuyến nghị.
        """
        if not raw_data:
            return {"error": "Không có dữ liệu chất lượng không khí."}

        current = raw_data.get("current", {})
        
        pm25 = current.get("pm2_5")
        pm10 = current.get("pm10")
        co = current.get("carbon_monoxide")
        no2 = current.get("nitrogen_dioxide")
        o3 = current.get("ozone")
        so2 = current.get("sulphur_dioxide")
        us_aqi_reported = current.get("us_aqi")

        # 1. Tính toán Sub-index từng chất
        sub_indices = {
            "pm2_5": calculate_aqi_subindex("pm2_5", pm25),
            "pm10": calculate_aqi_subindex("pm10", pm10),
            "ozone": calculate_aqi_subindex("ozone", o3),
            "nitrogen_dioxide": calculate_aqi_subindex("nitrogen_dioxide", no2),
            "carbon_monoxide": calculate_aqi_subindex("carbon_monoxide", co),
            "sulphur_dioxide": calculate_aqi_subindex("sulphur_dioxide", so2),
        }

        # 2. Xác định AQI tổng hợp và chất ô nhiễm chủ đạo
        valid_sub_indices = {k: v for k, v in sub_indices.items() if v is not None}
        
        if valid_sub_indices:
            dominant_key = max(valid_sub_indices, key=valid_sub_indices.get)
            calc_max_aqi = valid_sub_indices[dominant_key]
        else:
            dominant_key = "us_aqi"
            calc_max_aqi = us_aqi_reported or 0

        final_aqi = max(calc_max_aqi, us_aqi_reported) if us_aqi_reported else calc_max_aqi

        # Tên hiển thị của chất ô nhiễm chủ đạo
        pollutant_display_names = {
            "pm2_5": "Bụi mịn PM2.5",
            "pm10": "Bụi PM10",
            "ozone": "Khí Ozone (O3)",
            "nitrogen_dioxide": "Khí Nitrogen Dioxide (NO2)",
            "carbon_monoxide": "Khí Carbon Monoxide (CO)",
            "sulphur_dioxide": "Khí Sulphur Dioxide (SO2)",
            "us_aqi": "Tổng hợp"
        }

        dominant_pollutant_name = pollutant_display_names.get(dominant_key, dominant_key)

        # 3. Phân cấp mức độ ô nhiễm và khuyến nghị y tế
        level_details = get_aqi_level_details(final_aqi)

        # 4. Chi tiết các chất ô nhiễm
        pollutants_detail = {
            "pm2_5": {
                "name": "Bụi mịn PM2.5",
                "value": pm25,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("pm2_5"),
                "description": "Hạt bụi siêu nhỏ có thể đi sâu vào phổi và phế nang."
            },
            "pm10": {
                "name": "Bụi PM10",
                "value": pm10,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("pm10"),
                "description": "Hạt bụi lơ lửng kích thước dưới 10 micromet gây kích ứng hô hấp."
            },
            "carbon_monoxide": {
                "name": "Khí CO (Carbon Monoxide)",
                "value": co,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("carbon_monoxide"),
                "description": "Khí không màu không mùi phát sinh từ quá trình đốt không hoàn toàn."
            },
            "nitrogen_dioxide": {
                "name": "Khí NO2 (Nitrogen Dioxide)",
                "value": no2,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("nitrogen_dioxide"),
                "description": "Khí thải từ phương tiện giao thông và các nhà máy nhiệt điện."
            },
            "ozone": {
                "name": "Khí O3 (Ozone mặt đất)",
                "value": o3,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("ozone"),
                "description": "Khí sinh ra từ phản ứng quang hóa khi có ánh nắng mặt trời gắt."
            },
            "sulphur_dioxide": {
                "name": "Khí SO2 (Sulphur Dioxide)",
                "value": so2,
                "unit": "μg/m³",
                "sub_index": sub_indices.get("sulphur_dioxide"),
                "description": "Khí lưu huỳnh gây kích thích mắt và niêm mạc phế quản."
            }
        }

        # 5. Khuyến nghị hành động cụ thể
        action_guide = {
            "outdoor_exercise": "Nên tập" if final_aqi <= 100 else ("Hạn chế tập cường độ cao" if final_aqi <= 150 else "Không nên tập ngoài trời"),
            "wear_mask": "Cần thiết (khẩu trang N95 hoặc chống bụi mịn)" if level_details["mask_needed"] else "Không bắt buộc",
            "open_windows": "Có thể mở cửa đón gió tự nhiên" if final_aqi <= 100 else "Nên đóng kín cửa sổ để tránh bụi vào nhà",
            "air_purifier": "Nên bật liên tục trong phòng" if level_details["air_purifier_needed"] else "Không nhất thiết, có thể bật định kỳ"
        }

        result = {
            "aqi": final_aqi,
            "level": level_details["level"],
            "category": level_details["category"],
            "color": level_details["color"],
            "icon": level_details["icon"],
            "severity": level_details["severity"],
            "dominant_pollutant": dominant_pollutant_name,
            "description": level_details["description"],
            "health_effects": level_details["health_effects"],
            "health_recommendations": {
                "general_public": level_details["general_recommendation"],
                "sensitive_groups": level_details["sensitive_recommendation"]
            },
            "action_guide": action_guide,
            "pollutants": pollutants_detail
        }

        return clean_numpy_types(result)
