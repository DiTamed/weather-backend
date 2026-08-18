import math
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def clean_numpy_types(obj: Any) -> Any:
    """
    Đệ quy chuyển đổi các kiểu dữ liệu Numpy (int64, float64...)
    và Pandas (NaN, Timestamp) về kiểu chuẩn của Python.
    """
    if isinstance(obj, dict):
        return {k: clean_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_types(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")
    elif pd.isna(obj):
        return None
    return obj


# =====================================================================
# WMO WEATHER CODE MAPPING
# =====================================================================
WMO_WEATHER_CODES: Dict[int, Dict[str, str]] = {
    0: {"name": "Trời quang đãng", "category": "clear", "icon": "☀️"},
    1: {"name": "Hầu như quang đãng", "category": "mainly_clear", "icon": "🌤️"},
    2: {"name": "Có mây một phần", "category": "partly_cloudy", "icon": "⛅"},
    3: {"name": "Trời nhiều mây u ám", "category": "overcast", "icon": "☁️"},
    45: {"name": "Sương mù", "category": "fog", "icon": "🌫️"},
    48: {"name": "Sương mù đóng băng", "category": "fog", "icon": "🌫️"},
    51: {"name": "Mưa phùn nhẹ", "category": "drizzle", "icon": "🌦️"},
    53: {"name": "Mưa phùn vừa", "category": "drizzle", "icon": "🌧️"},
    55: {"name": "Mưa phùn dày đặc", "category": "drizzle", "icon": "🌧️"},
    56: {"name": "Mưa phùn buốt giá nhẹ", "category": "drizzle", "icon": "🌨️"},
    57: {"name": "Mưa phùn buốt giá đặc", "category": "drizzle", "icon": "🌨️"},
    61: {"name": "Mưa rào nhẹ", "category": "rain", "icon": "🌦️"},
    63: {"name": "Mưa vừa", "category": "rain", "icon": "🌧️"},
    65: {"name": "Mưa to", "category": "heavy_rain", "icon": "🌧️"},
    66: {"name": "Mưa buốt nhẹ", "category": "rain", "icon": "🌨️"},
    67: {"name": "Mưa buốt to", "category": "heavy_rain", "icon": "🌨️"},
    71: {"name": "Tuyết rơi nhẹ", "category": "snow", "icon": "🌨️"},
    73: {"name": "Tuyết rơi vừa", "category": "snow", "icon": "❄️"},
    75: {"name": "Tuyết rơi dày đặc", "category": "heavy_snow", "icon": "❄️"},
    77: {"name": "Tuyết hạt", "category": "snow", "icon": "🌨️"},
    80: {"name": "Mưa rào thoáng qua nhẹ", "category": "rain_shower", "icon": "🌦️"},
    81: {"name": "Mưa rào rải rác", "category": "rain_shower", "icon": "🌧️"},
    82: {"name": "Mưa rào rất to và xối xả", "category": "heavy_rain", "icon": "⛈️"},
    85: {"name": "Mưa tuyết nhẹ", "category": "snow", "icon": "🌨️"},
    86: {"name": "Mưa tuyết to", "category": "snow", "icon": "❄️"},
    95: {"name": "Dông bão kèm mưa", "category": "thunderstorm", "icon": "⛈️"},
    96: {"name": "Dông bão kèm mưa đá nhẹ", "category": "thunderstorm", "icon": "⛈️"},
    99: {"name": "Dông bão kèm mưa đá to", "category": "thunderstorm", "icon": "⚡"},
}


def get_weather_code_info(code: Optional[int]) -> Dict[str, str]:
    if code is None:
        return {"name": "Không xác định", "category": "unknown", "icon": "🌡️"}
    return WMO_WEATHER_CODES.get(
        code,
        {"name": f"Thời tiết (Mã {code})", "category": "general", "icon": "🌤️"}
    )


# =====================================================================
# CLIMATE REGION & SEASON DETERMINATION
# =====================================================================
def get_climate_region(lat: float, lon: float, location_name: str = "") -> Dict[str, str]:
    """
    Xác định vùng khí hậu và sinh thái nông nghiệp tại Việt Nam.
    """
    name_lower = location_name.lower()
    
    # Check by popular names or coordinates
    if any(k in name_lower for k in ["hà nội", "ha noi", "hải phòng", "hai phong", "quảng ninh", "bắc ninh", "hải dương", "nam định", "ninh bình", "thái bình", "vĩnh phúc", "phú thọ"]):
        return {"id": "bac_bo", "name": "Đồng bằng Sông Hồng & Bắc Bộ", "type": "Nhiệt đới gió mùa có mùa đông lạnh"}
    
    if any(k in name_lower for k in ["thái nguyên", "lạng sơn", "cao bằng", "hà giang", "tuyên quang", "bắc kạn", "lào cai", "yên bái", "lai châu", "điện biên", "sơn la", "hòa bình"]):
        return {"id": "tay_bac_dong_bac", "name": "Trung du & Miền núi phía Bắc", "type": "Cận nhiệt đới vùng núi, mùa đông lạnh giá"}
        
    if any(k in name_lower for k in ["đà lạt", "da lat", "lâm đồng", "lam dong", "đắk lắk", "dak lak", "gia lai", "kon tum", "đắk nông", "dak nong"]):
        return {"id": "tay_nguyen", "name": "Tây Nguyên & Cao Nguyên", "type": "Khí hậu cao nguyên 2 mùa mưa - khô rõ rệt, mát mẻ"}
        
    if any(k in name_lower for k in ["đà nẵng", "da nang", "huế", "hue", "quảng nam", "quảng ngãi", "bình định", "phú yên", "khánh hòa", "nha trang", "ninh thuận", "bình thuận", "quảng bình", "quảng trị", "hà tĩnh", "nghệ an", "thanh hóa"]):
        return {"id": "trung_bo", "name": "Duyên hải Miền Trung", "type": "Nhiệt đới gió mùa, chịu ảnh hưởng bão lũ và gió phơn tây nam"}
        
    if any(k in name_lower for k in ["hồ chí minh", "ho chi minh", "sài gòn", "sai gon", "bình dương", "đồng nai", "bà rịa", "vũng tàu", "tây ninh", "bình phước"]):
        return {"id": "dong_nam_bo", "name": "Đông Nam Bộ", "type": "Nhiệt đới cận xích đạo, 2 mùa mưa - khô"}
        
    if any(k in name_lower for k in ["cần thơ", "can tho", "long an", "tiền giang", "bến tre", "trà vinh", "vĩnh long", "đồng tháp", "an giang", "kiên giang", "hậu giang", "sóc trăng", "bạc liêu", "cà mau"]):
        return {"id": "tay_nam_bo", "name": "Đồng bằng Sông Cửu Long (Tây Nam Bộ)", "type": "Nhiệt đới gió mùa cận xích đạo, đất phù sa ngập mặn và mùa nước nổi"}

    # Coordinate heuristic for Vietnam
    if lat >= 19.5:
        return {"id": "bac_bo", "name": "Khu vực Bắc Bộ", "type": "Nhiệt đới gió mùa có mùa đông lạnh"}
    elif lat >= 15.5:
        return {"id": "bac_trung_bo", "name": "Khu vực Bắc & Trung Trung Bộ", "type": "Nhiệt đới gió mùa miền Trung"}
    elif lat >= 11.5 and lon <= 108.5:
        return {"id": "tay_nguyen", "name": "Khu vực Cao nguyên & Tây Nguyên", "type": "Khí hậu cao nguyên, 2 mùa mưa - khô"}
    elif lat >= 11.5:
        return {"id": "nam_trung_bo", "name": "Duyên hải Nam Trung Bộ", "type": "Nhiệt đới gió mùa ven biển"}
    else:
        return {"id": "nam_bo", "name": "Khu vực Nam Bộ", "type": "Nhiệt đới cận xích đạo, nền nhiệt cao quanh năm"}


def get_season_info(month: int, region_id: str) -> Dict[str, str]:
    """
    Xác định mùa khí hậu theo tháng và vùng miền.
    """
    if region_id in ["bac_bo", "tay_bac_dong_bac", "bac_trung_bo"]:
        if month in [12, 1, 2]:
            return {"season": "Mùa Đông", "description": "Thời tiết lạnh, ít mưa, thỉnh thoảng có sương muối hoặc rét hại."}
        elif month in [3, 4]:
            return {"season": "Mùa Xuân", "description": "Thời tiết ấm dần, độ ẩm cao, có mưa phùn và hiện tượng nồm ẩm."}
        elif month in [5, 6, 7, 8]:
            return {"season": "Mùa Hạ", "description": "Thời tiết nóng ẩm, bức xạ nhiệt cao, nhiều mưa rào và dông bão."}
        else:
            return {"season": "Mùa Thu", "description": "Thời tiết mát mẻ, trời trong xanh, khô ráo, nhiệt độ ôn hòa."}
    else:
        # Nam Bộ, Tây Nguyên, Nam Trung Bộ
        if 5 <= month <= 11:
            return {"season": "Mùa Mưa", "description": "Thời tiết nhiều mưa rào, độ ẩm không khí cao, nhiệt độ duy trì 26-33°C."}
        else:
            return {"season": "Mùa Khô", "description": "Nắng nhiều, bức xạ mạnh, độ ẩm thấp, cần chú ý nguồn nước tưới tiêu."}


# =====================================================================
# WIND SPEED (KM/H) & BEAUFORT CATEGORIZATION
# =====================================================================
def get_wind_scale(speed_kmh: float) -> Dict[str, Any]:
    """
    Phân loại cấp gió theo thang Beaufort từ tốc độ gió km/h (chuẩn Open-Meteo).
    """
    if speed_kmh < 2:
        return {"level": 0, "name": "Gió lặng", "desc": "Khói bốc thẳng, mặt nước phẳng lặng."}
    elif speed_kmh < 6:
        return {"level": 1, "name": "Gió nhẹ thoảng", "desc": "Khói nghiêng nhẹ, lá cây khẽ lay."}
    elif speed_kmh < 12:
        return {"level": 2, "name": "Gió nhẹ", "desc": "Cảm nhận được gió trên mặt, lá xào xạc."}
    elif speed_kmh < 20:
        return {"level": 3, "name": "Gió êm dịu", "desc": "Lá và cành nhỏ rung rinh, cờ bay nhẹ."}
    elif speed_kmh < 29:
        return {"level": 4, "name": "Gió vừa phải", "desc": "Bụi cát bay, cành cây nhỏ chuyển động."}
    elif speed_kmh < 39:
        return {"level": 5, "name": "Gió khá mạnh", "desc": "Cây nhỏ đung đưa, sóng lăn tăn trên hồ."}
    elif speed_kmh < 50:
        return {"level": 6, "name": "Gió mạnh", "desc": "Cành cây lớn rung chuyển, khó dùng ô/dù."}
    elif speed_kmh < 62:
        return {"level": 7, "name": "Gió rất mạnh (Gần bão)", "desc": "Cây cối ngả nghiêng, khó đi bộ ngược gió."}
    elif speed_kmh < 75:
        return {"level": 8, "name": "Gió giật dữ dội (Gió bão nhẹ)", "desc": "Gãy cành cây nhỏ, cản trở giao thông."}
    elif speed_kmh < 89:
        return {"level": 9, "name": "Gió bão mạnh", "desc": "Tốc mái nhà, cây cối có thể gãy đổ."}
    else:
        return {"level": 10, "name": "Bão rất mạnh / Cuồng phong", "desc": "Nguy hiểm cực độ, tàn phá nghiêm trọng."}


# =====================================================================
# EPA / VN AQI STANDARD CALCULATION
# =====================================================================
# Breakpoint table: (C_low, C_high, I_low, I_high)
AQI_BREAKPOINTS = {
    "pm2_5": [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ],
    "pm10": [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500),
    ],
    "ozone": [
        (0, 100, 0, 50),
        (101, 160, 51, 100),
        (161, 215, 101, 150),
        (216, 265, 151, 200),
        (266, 800, 201, 300),
    ],
    "nitrogen_dioxide": [
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
    ],
    "carbon_monoxide": [
        (0, 4400, 0, 50),
        (4401, 9400, 51, 100),
        (9401, 12400, 101, 150),
        (12401, 15400, 151, 200),
        (15401, 30400, 201, 300),
    ],
    "sulphur_dioxide": [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
    ]
}


def calculate_aqi_subindex(pollutant_name: str, concentration: Optional[float]) -> Optional[int]:
    """
    Tính chỉ số AQI thành phần (Sub-index Ip) cho từng chất ô nhiễm.
    Công thức: Ip = ((I_hi - I_lo) / (BP_hi - BP_lo)) * (Cp - BP_lo) + I_lo
    """
    if concentration is None or concentration < 0:
        return None
        
    breakpoints = AQI_BREAKPOINTS.get(pollutant_name)
    if not breakpoints:
        return None

    c = round(concentration, 1)
    
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= c <= bp_hi:
            ip = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (c - bp_lo) + i_lo
            return int(round(ip))
            
    # If concentration exceeds highest breakpoint
    if c > breakpoints[-1][1]:
        return 500
        
    return 0


def get_aqi_level_details(aqi_val: int) -> Dict[str, Any]:
    """
    Xác định mức độ chất lượng không khí, màu sắc và khuyến nghị sức khỏe tiêu chuẩn.
    """
    if aqi_val <= 50:
        return {
            "level": "Tốt",
            "category": "Good",
            "color": "#00E400",
            "icon": "🟢",
            "severity": "SAFE",
            "description": "Chất lượng không khí đạt chuẩn, trong lành và an toàn.",
            "health_effects": "Không gây ảnh hưởng tới sức khỏe.",
            "general_recommendation": "Tự do tham gia các hoạt động ngoài trời, thông gió tự nhiên tốt cho nhà cửa.",
            "sensitive_recommendation": "Không cần biện pháp phòng ngừa đặc biệt.",
            "mask_needed": False,
            "air_purifier_needed": False
        }
    elif aqi_val <= 100:
        return {
            "level": "Trung bình",
            "category": "Moderate",
            "color": "#FFFF00",
            "icon": "🟡",
            "severity": "INFO",
            "description": "Chất lượng không khí ở mức chấp nhận được.",
            "health_effects": "Có thể gây một số phản ứng nhẹ cho nhóm người cực kỳ nhạy cảm với bụi và khói.",
            "general_recommendation": "Có thể duy trì các hoạt động bình thường ngoài trời.",
            "sensitive_recommendation": "Nhóm người bị hen suyễn hoặc mẫn cảm nên theo dõi cơ thể khi vận động mạnh ngoài trời.",
            "mask_needed": False,
            "air_purifier_needed": False
        }
    elif aqi_val <= 150:
        return {
            "level": "Kém (Kém cho nhóm nhạy cảm)",
            "category": "Unhealthy for Sensitive Groups",
            "color": "#FF7E00",
            "icon": "🟠",
            "severity": "WARNING",
            "description": "Không khí bắt đầu bị ô nhiễm, ảnh hưởng rõ rệt tới đối tượng dễ tổn thương.",
            "health_effects": "Trẻ em, người già và người mắc bệnh hô hấp/tim mạch có thể bị khó thở, ho, tức ngực.",
            "general_recommendation": "Người bình thường vẫn sinh hoạt được nhưng nên hạn chế vận động thể lực kéo dài ngoài trời.",
            "sensitive_recommendation": "Nên giảm thời gian ra ngoài, đeo khẩu trang lọc bụi khi ra đường.",
            "mask_needed": True,
            "air_purifier_needed": True
        }
    elif aqi_val <= 200:
        return {
            "level": "Xấu (Có hại cho sức khỏe)",
            "category": "Unhealthy",
            "color": "#FF0000",
            "icon": "🔴",
            "severity": "WARNING",
            "description": "Mức độ ô nhiễm cao, ảnh hưởng đến sức khỏe của tất cả mọi người.",
            "health_effects": "Gia tăng kích ứng mắt, mũi họng, suy giảm chức năng phổi ở người khỏe mạnh; nguy hiểm cho người có tiền sử hô hấp.",
            "general_recommendation": "Tránh tập thể dục ngoài trời, đóng cửa sổ, đeo khẩu trang N95 hoặc khẩu trang chống bụi mịn khi ra ngoài.",
            "sensitive_recommendation": "Tránh hoàn toàn các hoạt động ngoài trời, ở trong phòng kín có bật máy lọc không khí.",
            "mask_needed": True,
            "air_purifier_needed": True
        }
    elif aqi_val <= 300:
        return {
            "level": "Rất xấu (Rất có hại)",
            "category": "Very Unhealthy",
            "color": "#8F3F97",
            "icon": "🟣",
            "severity": "CRITICAL",
            "description": "Cảnh báo khẩn cấp về sức khỏe toàn cộng đồng do nồng độ bụi và khí độc rất cao.",
            "health_effects": "Toàn bộ người dân có nguy cơ bị ảnh hưởng nghiêm trọng đến hệ hô hấp và tim mạch.",
            "general_recommendation": "Hạn chế tối đa ra ngoài đường, đóng kín các cửa sổ và cửa thông gió, mở máy lọc không khí liên tục.",
            "sensitive_recommendation": "Tuyệt đối không ra ngoài, nếu xuất hiện triệu chứng khó thở cần liên hệ y tế ngay.",
            "mask_needed": True,
            "air_purifier_needed": True
        }
    else:
        return {
            "level": "Nguy hại (Báo động)",
            "category": "Hazardous",
            "color": "#7E0023",
            "icon": "🟤",
            "severity": "CRITICAL",
            "description": "Mức độ ô nhiễm nghiêm trọng đe dọa trực tiếp đến tính mạng con người.",
            "health_effects": "Mọi người có thể bị ngộ độc không khí, tổn thương phổi cấp tính.",
            "general_recommendation": "Tất cả mọi người nên ở trong nhà kín có hệ thống lọc khí chuyên dụng, đeo mặt nạ phòng độc/N95 nếu bắt buộc ra ngoài.",
            "sensitive_recommendation": "Theo dõi sát sao sức khỏe người cao tuổi và trẻ nhỏ, tuân thủ hướng dẫn khẩn cấp.",
            "mask_needed": True,
            "air_purifier_needed": True
        }
