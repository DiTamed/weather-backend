from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from app.utils.calculations import (
    get_climate_region,
    get_season_info,
    clean_numpy_types
)


# =====================================================================
# CROP DATABASE (AGRONOMIC KNOWLEDGE BASE FOR VIETNAM)
# =====================================================================
CROPS_DATABASE = {
    "lua_nuoc": {
        "name": "Lúa nước (Lúa vụ)",
        "category": "Cây lương thực",
        "icon": "🌾",
        "temp_range": (20.0, 35.0),
        "opt_temp": (24.0, 32.0),
        "hum_range": (60.0, 95.0),
        "rain_range": (80.0, 300.0), # mm / tháng hoặc chu kỳ
        "suitable_regions": ["bac_bo", "tay_nam_bo", "dong_nam_bo", "trung_bo", "bac_trung_bo"],
        "care_tips": "Đảm bảo mực nước 3-5cm thời kỳ đẻ nhánh; rút nước phơi ruộng trước khi trổ.",
        "disease_risk": "Độ ẩm cao trên 85% kèm nhiệt độ 26-30°C dễ phát sinh bệnh đạo ôn, rầy nâu và bạc lá."
    },
    "ngo": {
        "name": "Ngô (Bắp lai/Bắp ngọt)",
        "category": "Cây lương thực & hoa màu",
        "icon": "🌽",
        "temp_range": (18.0, 34.0),
        "opt_temp": (22.0, 30.0),
        "hum_range": (55.0, 85.0),
        "rain_range": (40.0, 150.0),
        "suitable_regions": ["bac_bo", "tay_bac_dong_bac", "tay_nguyen", "dong_nam_bo", "trung_bo"],
        "care_tips": "Cần đất thoát nước tốt; tưới đủ ẩm giai đoạn trổ cờ phun râu, tránh ngập úng gốc.",
        "disease_risk": "Ẩm ướt kéo dài dễ bị sâu keo mùa thu và bệnh đốm lá lớn."
    },
    "ca_phe": {
        "name": "Cà phê (Robusta / Arabica)",
        "category": "Cây công nghiệp lâu năm",
        "icon": "☕",
        "temp_range": (16.0, 30.0),
        "opt_temp": (20.0, 27.0),
        "hum_range": (65.0, 90.0),
        "rain_range": (60.0, 220.0),
        "suitable_regions": ["tay_nguyen", "dong_nam_bo", "tay_bac_dong_bac"],
        "care_tips": "Cần xiết nước tạo mầm hoa trong mùa khô và tưới bừng đón hoa nở; làm bồn giữ ẩm.",
        "disease_risk": "Mùa mưa kéo dài dễ phát sinh bệnh rỉ sắt và mọt đục cành."
    },
    "cao_su": {
        "name": "Cao su",
        "category": "Cây công nghiệp lâu năm",
        "icon": "🌳",
        "temp_range": (22.0, 34.0),
        "opt_temp": (25.0, 30.0),
        "hum_range": (70.0, 95.0),
        "rain_range": (100.0, 250.0),
        "suitable_regions": ["dong_nam_bo", "tay_nguyen", "bac_trung_bo"],
        "care_tips": "Không cạo mủ khi trời mưa hoặc cây còn ướt thân; bón phân cân đối N-P-K sau mùa rụng lá.",
        "disease_risk": "Độ ẩm cao gây bệnh phấn trắng và nấm hồng vỏ thân."
    },
    "che": {
        "name": "Cây chè (Trà xanh/Oolong)",
        "category": "Cây công nghiệp",
        "icon": "🍵",
        "temp_range": (15.0, 28.0),
        "opt_temp": (18.0, 24.0),
        "hum_range": (75.0, 95.0),
        "rain_range": (80.0, 200.0),
        "suitable_regions": ["tay_bac_dong_bac", "tay_nguyen", "bac_bo"],
        "care_tips": "Thích hợp vùng khí hậu mát mẻ nhiều sương mù; cần tủ gốc giữ ẩm bằng rơm rạ.",
        "disease_risk": "Cảnh báo rầy xanh và bọ xít muỗi khi thời tiết ấm ẩm chuyển mùa."
    },
    "sau_rieng": {
        "name": "Sầu riêng (Ri6, Monthong)",
        "category": "Cây ăn trái giá trị cao",
        "icon": "🍈",
        "temp_range": (24.0, 35.0),
        "opt_temp": (26.0, 32.0),
        "hum_range": (65.0, 85.0),
        "rain_range": (50.0, 180.0),
        "suitable_regions": ["tay_nguyen", "dong_nam_bo", "tay_nam_bo"],
        "care_tips": "Đặc biệt nhạy cảm với úng nước; cần hệ thống đắp mô cao và thoát nước nhanh trong mùa mưa.",
        "disease_risk": "Nấm Phytophthora gây xì mủ thối thân khi độ ẩm đất quá cao."
    },
    "xoai": {
        "name": "Xoài (Cát Chu, Cát Hòa Lộc)",
        "category": "Cây ăn trái",
        "icon": "🥭",
        "temp_range": (22.0, 36.0),
        "opt_temp": (25.0, 32.0),
        "hum_range": (55.0, 80.0),
        "rain_range": (30.0, 140.0),
        "suitable_regions": ["tay_nam_bo", "dong_nam_bo", "nam_trung_bo"],
        "care_tips": "Cần mùa khô rõ rệt để phân hóa mầm hoa; tránh mưa rào đúng đợt thụ phấn.",
        "disease_risk": "Bệnh thán thư gây đen bông rụng quả non khi có sương đêm hoặc mưa rải rác."
    },
    "thanh_long": {
        "name": "Thanh long",
        "category": "Cây ăn trái nhiệt đới",
        "icon": "🐉",
        "temp_range": (22.0, 38.0),
        "opt_temp": (26.0, 34.0),
        "hum_range": (50.0, 80.0),
        "rain_range": (20.0, 120.0),
        "suitable_regions": ["nam_trung_bo", "dong_nam_bo", "tay_nam_bo"],
        "care_tips": "Ưa nhiều nắng, chịu hạn tốt; chong đèn ban đêm trong mùa nghịch để kích thích ra hoa.",
        "disease_risk": "Bệnh đốm nâu (tắc kè) phát triển mạnh trong mùa mưa dầm ẩm ướt."
    },
    "ca_chua": {
        "name": "Cà chua (Rau màu quả)",
        "category": "Rau màu thương phẩm",
        "icon": "🍅",
        "temp_range": (16.0, 29.0),
        "opt_temp": (19.0, 25.0),
        "hum_range": (60.0, 80.0),
        "rain_range": (30.0, 100.0),
        "suitable_regions": ["tay_nguyen", "bac_bo", "tay_bac_dong_bac", "dong_nam_bo"],
        "care_tips": "Làm giàn vững chắc, tỉa bớt nhánh phụ; tưới nhỏ giọt vào gốc tránh ướt lá.",
        "disease_risk": "Bệnh mốc sương và héo xanh vi khuẩn khi nhiệt độ ban đêm mát ẩm kéo dài."
    },
    "rau_cai": {
        "name": "Rau cải (Cải ngọt, bắp cải, cải thìa)",
        "category": "Rau ăn lá ngắn ngày",
        "icon": "🥬",
        "temp_range": (14.0, 28.0),
        "opt_temp": (17.0, 24.0),
        "hum_range": (60.0, 90.0),
        "rain_range": (20.0, 100.0),
        "suitable_regions": ["bac_bo", "tay_nguyen", "tay_bac_dong_bac", "tay_nam_bo", "dong_nam_bo"],
        "care_tips": "Vụ đông xuân cho năng suất cao nhất; cần che lưới chắn mưa lớn làm giập nát lá.",
        "disease_risk": "Sâu tơ, bọ nhảy và bệnh thối nhũn lá trong môi trường ẩm cao."
    },
    "dua_leo": {
        "name": "Dưa chuột / Dưa leo",
        "category": "Rau màu quả ngắn ngày",
        "icon": "🥒",
        "temp_range": (20.0, 32.0),
        "opt_temp": (22.0, 28.0),
        "hum_range": (60.0, 85.0),
        "rain_range": (30.0, 120.0),
        "suitable_regions": ["bac_bo", "dong_nam_bo", "tay_nam_bo", "tay_nguyen", "trung_bo"],
        "care_tips": "Làm giàn chữ A; tưới nước đều đặn mỗi ngày vào sáng sớm hoặc chiều mát.",
        "disease_risk": "Bệnh phấn trắng và bọ trĩ phá hoại ngọn non khi trời oi nóng."
    }
}


class AgricultureService:
    """
    BE 3 - Trụ cột 1: Nông nghiệp thông minh (Smart Agriculture Recommendation Engine).
    Kết hợp Rule-Based Agronomic Engine và Machine Learning Classifier
    để gợi ý cây trồng, phân tích mức độ tương thích khí hậu, tưới tiêu và cảnh báo sâu bệnh.
    """

    _ml_model: Optional[RandomForestClassifier] = None
    _crop_classes: List[str] = list(CROPS_DATABASE.keys())

    @classmethod
    def _init_ml_model(cls):
        """
        Khởi tạo và huấn luyện mô hình Machine Learning phân loại cây trồng dựa trên dữ liệu khí hậu.
        Features: [temp_avg, temp_min, temp_max, humidity, rainfall_estimated, region_code, season_code]
        """
        if cls._ml_model is not None:
            return

        region_map = {"bac_bo": 0, "tay_bac_dong_bac": 1, "trung_bo": 2, "bac_trung_bo": 3, "nam_trung_bo": 4, "tay_nguyen": 5, "dong_nam_bo": 6, "tay_nam_bo": 7}
        season_map = {"Mùa Đông": 0, "Mùa Xuân": 1, "Mùa Hạ": 2, "Mùa Thu": 3, "Mùa Mưa": 4, "Mùa Khô": 5}

        # Tạo tập dữ liệu huấn luyện tổng hợp (Synthetic Agronomic Climate Distribution)
        np.random.seed(42)
        X_train = []
        y_train = []

        for crop_id, data in CROPS_DATABASE.items():
            t_min_bound, t_max_bound = data["temp_range"]
            t_opt_low, t_opt_high = data["opt_temp"]
            h_min, h_max = data["hum_range"]
            r_min, r_max = data["rain_range"]
            suitable_regs = data["suitable_regions"]

            for _ in range(80):
                # Sample optimal conditions
                t_avg = np.random.uniform(t_opt_low - 1.5, t_opt_high + 1.5)
                t_min = t_avg - np.random.uniform(4.0, 9.0)
                t_max = t_avg + np.random.uniform(4.0, 9.0)
                hum = np.random.uniform(h_min, h_max)
                rain = np.random.uniform(r_min, r_max)
                
                reg = np.random.choice(suitable_regs)
                reg_code = region_map.get(reg, 0)
                
                if reg in ["bac_bo", "tay_bac_dong_bac", "bac_trung_bo"]:
                    if t_avg < 20:
                        s_code = 0 # Dong
                    elif t_avg < 25:
                        s_code = 1 # Xuan
                    elif t_avg > 28:
                        s_code = 2 # Ha
                    else:
                        s_code = 3 # Thu
                else:
                    s_code = 4 if rain > 120 else 5 # Mua / Kho

                X_train.append([t_avg, t_min, t_max, hum, rain, reg_code, s_code])
                y_train.append(crop_id)

        cls._ml_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
        cls._ml_model.fit(X_train, y_train)

    @classmethod
    def recommend_crops(
        cls,
        lat: float,
        lon: float,
        city_name: str,
        weather_analysis: Dict[str, Any],
        current_weather: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Đề xuất cây trồng thông minh dựa trên phân tích nhiệt độ, lượng mưa, độ ẩm, mùa vụ và vị trí địa lý.
        """
        cls._init_ml_model()

        # 1. Xác định Vị trí & Vùng khí hậu
        region_info = get_climate_region(lat, lon, city_name)
        now = datetime.now()
        season_info = get_season_info(now.month, region_info["id"])

        # 2. Thu thập các chỉ số thời tiết
        temp_data = weather_analysis.get("temperature_analysis", {})
        rain_data = weather_analysis.get("precipitation_analysis", {})
        hum_data = weather_analysis.get("humidity_analysis", {})

        avg_temp = temp_data.get("avg_temp", 27.0)
        min_temp = temp_data.get("min_temp", 23.0)
        max_temp = temp_data.get("max_temp", 32.0)
        
        # Quy đổi tổng lượng mưa 15 ngày sang ước lượng lượng mưa chu kỳ/tháng
        total_15d_rain = rain_data.get("total_rain", 20.0)
        monthly_rain_est = total_15d_rain * 2.0
        avg_hum = hum_data.get("avg_humidity", 75.0)

        # 3. Tính toán bằng Machine Learning Model
        region_map = {"bac_bo": 0, "tay_bac_dong_bac": 1, "trung_bo": 2, "bac_trung_bo": 3, "nam_trung_bo": 4, "tay_nguyen": 5, "dong_nam_bo": 6, "tay_nam_bo": 7}
        season_map = {"Mùa Đông": 0, "Mùa Xuân": 1, "Mùa Hạ": 2, "Mùa Thu": 3, "Mùa Mưa": 4, "Mùa Khô": 5}
        
        reg_code = region_map.get(region_info["id"], 0)
        s_code = season_map.get(season_info["season"], 4)

        features = np.array([[avg_temp, min_temp, max_temp, avg_hum, monthly_rain_est, reg_code, s_code]])
        ml_probs = cls._ml_model.predict_proba(features)[0]
        ml_prob_dict = {cls._ml_model.classes_[i]: float(ml_probs[i]) for i in range(len(ml_probs))}

        # 4. Tính toán kết hợp Rule-Based Agronomic Evaluation
        crop_evaluations: List[Dict[str, Any]] = []

        for crop_id, data in CROPS_DATABASE.items():
            rule_score = 100.0
            reasons = []

            # Đánh giá nhiệt độ
            t_min, t_max = data["temp_range"]
            t_opt_low, t_opt_high = data["opt_temp"]
            
            if t_opt_low <= avg_temp <= t_opt_high:
                rule_score += 10
                reasons.append(f"Nhiệt độ {avg_temp}°C trong ngưỡng tối ưu sinh trưởng ({t_opt_low}-{t_opt_high}°C).")
            elif t_min <= avg_temp <= t_max:
                rule_score -= 10
                reasons.append(f"Nhiệt độ {avg_temp}°C trong ngưỡng chấp nhận được.")
            else:
                rule_score -= 45
                reasons.append(f"Nhiệt độ {avg_temp}°C nằm ngoài dải chịu đựng ({t_min}-{t_max}°C).")

            # Đánh giá độ ẩm
            h_min, h_max = data["hum_range"]
            if h_min <= avg_hum <= h_max:
                rule_score += 5
            else:
                rule_score -= 20
                reasons.append(f"Độ ẩm {avg_hum}% không lý tưởng (yêu cầu {h_min}-{h_max}%).")

            # Đánh giá lượng mưa
            r_min, r_max = data["rain_range"]
            if r_min <= monthly_rain_est <= r_max:
                rule_score += 5
            elif monthly_rain_est < r_min:
                rule_score -= 15
                reasons.append(f"Lượng mưa ước tính {monthly_rain_est:.0f}mm/tháng thấp hơn nhu cầu cây trồng.")
            else:
                rule_score -= 25
                reasons.append(f"Lượng mưa ước tính {monthly_rain_est:.0f}mm/tháng cao, nguy cơ ngập úng.")

            # Đánh giá vùng sinh thái
            if region_info["id"] in data["suitable_regions"]:
                rule_score += 10
                reasons.append(f"Phù hợp đặc trưng thổ nhưỡng vùng {region_info['name']}.")
            else:
                rule_score -= 30
                reasons.append(f"Ít phổ biến tại vùng {region_info['name']}.")

            # Kết hợp điểm Rule-Based (60%) và Machine Learning Probability (40%)
            ml_p = ml_prob_dict.get(crop_id, 0.0)
            ml_scaled_score = min(100.0, ml_p * 350.0) # Scale probability to score

            final_suitability = round(max(5.0, min(98.0, 0.6 * rule_score + 0.4 * ml_scaled_score)), 1)

            if final_suitability >= 80.0:
                fit_level = "Rất thích hợp"
            elif final_suitability >= 65.0:
                fit_level = "Thích hợp"
            elif final_suitability >= 45.0:
                fit_level = "Cần chăm sóc kỹ"
            else:
                fit_level = "Không khuyến khích"

            crop_evaluations.append({
                "crop_id": crop_id,
                "name": data["name"],
                "category": data["category"],
                "icon": data["icon"],
                "suitability_score": final_suitability,
                "fit_level": fit_level,
                "reasons": reasons[:2],
                "care_tips": data["care_tips"],
                "disease_risk": data["disease_risk"]
            })

        # Sắp xếp cây trồng từ phù hợp nhất xuống thấp nhất
        crop_evaluations.sort(key=lambda x: x["suitability_score"], reverse=True)
        top_recommended = [c for c in crop_evaluations if c["suitability_score"] >= 60.0][:5]

        # 5. Hướng dẫn tưới tiêu & kỹ thuật canh tác tổng thể theo thời tiết
        if monthly_rain_est >= 150.0 or total_15d_rain >= 50.0:
            irrigation_plan = "Hạn chế tưới; khơi thông mương rãnh, nạo vét kênh mương phòng chống ngập úng gốc cây."
        elif monthly_rain_est <= 40.0:
            irrigation_plan = "Tăng cường tưới định kỳ 1-2 lần/ngày vào sáng sớm hoặc chiều mát; tủ gốc bằng rơm rạ hoặc màng phủ nông nghiệp."
        else:
            irrigation_plan = "Duy trì chế độ tưới ẩm tiêu chuẩn; tưới theo nhu cầu từng loại cây khi mặt đất se khô."

        # Cảnh báo rủi ro thời tiết cho nông nghiệp
        agri_alerts = []
        if max_temp >= 35.0:
            agri_alerts.append({
                "risk": "Nắng nóng / Sốc nhiệt",
                "severity": "WARNING",
                "message": "Nhiệt độ cao làm bốc thoát hơi nước nhanh, dễ cháy lá non và rụng hoa/trái non. Nên phun sương giải nhiệt."
            })
        if min_temp <= 14.0:
            agri_alerts.append({
                "risk": "Rét đậm / Sương muối",
                "severity": "WARNING",
                "message": "Nhiệt độ hạ thấp làm chậm quá trình quang hợp và sinh trưởng. Cần ủ ấm gốc và che chắn gió bắc."
            })
        if total_15d_rain >= 60.0:
            agri_alerts.append({
                "risk": "Mưa lớn / Ngập úng",
                "severity": "WARNING",
                "message": "Lượng mưa lớn có thể làm nghẹt rễ, rửa trôi phân bón. Cần kiểm tra hệ thống thoát nước sau mưa."
            })
        if avg_hum >= 85.0:
            agri_alerts.append({
                "risk": "Độ ẩm cao bùng phát dịch nấm & rầy",
                "severity": "INFO",
                "message": "Độ ẩm trên 85% là môi trường lý tưởng cho nấm bệnh (đạo ôn, thán thư, mốc sương) và rầy hại phát triển."
            })

        return clean_numpy_types({
            "location_info": {
                "city": city_name,
                "region": region_info["name"],
                "climate_type": region_info["type"],
                "current_season": season_info["season"],
                "season_description": season_info["description"]
            },
            "weather_summary": {
                "avg_temperature": avg_temp,
                "min_temperature": min_temp,
                "max_temperature": max_temp,
                "avg_humidity": avg_hum,
                "total_rain_15d": total_15d_rain,
                "estimated_monthly_rain": round(monthly_rain_est, 1)
            },
            "irrigation_and_soil_plan": irrigation_plan,
            "agricultural_weather_risks": agri_alerts,
            "top_recommended_crops": top_recommended,
            "all_crops_evaluation": crop_evaluations
        })
