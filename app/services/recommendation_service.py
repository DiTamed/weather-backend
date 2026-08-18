from typing import Dict, Any, List, Optional
from app.utils.calculations import (
    get_weather_code_info,
    get_wind_scale,
    clean_numpy_types
)


class RecommendationService:
    """
    BE 3 - Trụ cột 2: Gợi ý sinh hoạt & Tổng hợp khuyến nghị thông minh.
    Dựa vào Temperature, Feels Like, Rain Probability, Rainfall, Wind Speed,
    Weather Code và AQI để đưa ra khuyến nghị thực tế cho đời sống người dân.
    """

    @staticmethod
    def generate_lifestyle_recommendation(
        current_weather: Dict[str, Any],
        daily_weather: Optional[Dict[str, Any]] = None,
        air_quality: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tạo khuyến nghị sinh hoạt hàng ngày: Trang phục, Hoạt động ngoài trời, Sức khỏe, Giao thông.
        """
        temp = current_weather.get("temperature", 28.0)
        feels_like = current_weather.get("feels_like", temp)
        humidity = current_weather.get("humidity", 70.0)
        rain_amount = current_weather.get("precipitation", 0.0)
        wind_speed = current_weather.get("wind_speed", 10.0) # km/h
        weather_code = current_weather.get("weather_code", 0)

        # Lấy thêm thông tin từ daily nếu có
        rain_prob = 0.0
        if daily_weather:
            rain_prob = daily_weather.get("rain_probability", 0.0)
            if rain_amount == 0.0:
                rain_amount = daily_weather.get("precipitation", 0.0)

        aqi_val = air_quality.get("aqi", 45) if air_quality else 45
        aqi_level = air_quality.get("level", "Tốt") if air_quality else "Tốt"

        w_info = get_weather_code_info(weather_code)
        w_category = w_info.get("category", "clear")
        wind_info = get_wind_scale(wind_speed)

        # -------------------------------------------------------------
        # 1. GỢI Ý TRANG PHỤC (CLOTHING ADVICE)
        # -------------------------------------------------------------
        clothing_items = []
        clothing_summary = ""

        if feels_like <= 15.0:
            clothing_items.extend(["Áo khoác phao / áo ấm dày", "Áo len cổ lọ", "Khăn quàng cổ", "Quần dài giữ nhiệt"])
            clothing_summary = "Thời tiết rét buốt, cần mặc nhiều lớp áo ấm dày và giữ ấm cổ họng."
        elif feels_like <= 21.0:
            clothing_items.extend(["Áo khoác gió nhẹ", "Áo nỉ / Cardigan", "Quần jeans / quần dài"])
            clothing_summary = "Thời tiết mát mẻ se lạnh, nên mặc thêm một chiếc áo khoác mỏng."
        elif feels_like <= 29.0:
            clothing_items.extend(["Áo thun cotton thoáng mát", "Quần áo nhẹ nhàng", "Giày thể thao thoải mái"])
            clothing_summary = "Thời tiết dễ chịu, trang phục thoải mái thoáng khí."
        else:
            clothing_items.extend(["Trang phục mỏng nhẹ, thấm hút mồ hôi", "Áo khoác chống tia UV khi ra đường", "Kính râm", "Mũ rộng vành"])
            clothing_summary = f"Thời tiết nóng bức (cảm giác như {feels_like}°C), cần mặc đồ mát và che chắn tia cực tím."

        # Phụ kiện đi kèm theo mưa / nắng / AQI
        accessories = []
        if rain_prob >= 40 or rain_amount > 0.5 or w_category in ["rain", "heavy_rain", "thunderstorm", "drizzle"]:
            accessories.append("Mang theo ô (dù) hoặc áo mưa trong cốp xe")
            accessories.append("Giày chống nước hoặc bọc giày đi mưa")

        if aqi_val > 100:
            accessories.append("Đeo khẩu trang N95 chống bụi mịn PM2.5 khi ra đường")
        elif aqi_val > 50:
            accessories.append("Đeo khẩu trang y tế thông thường")

        if feels_like >= 32.0 and w_category in ["clear", "mainly_clear"]:
            accessories.append("Bôi kem chống nắng SPF 30+ trước khi ra ngoài")

        # -------------------------------------------------------------
        # 2. ĐÁNH GIÁ CÁC HOẠT ĐỘNG NGOÀI TRỜI (OUTDOOR ACTIVITIES)
        # -------------------------------------------------------------
        is_raining = rain_amount >= 1.0 or rain_prob >= 60 or w_category in ["rain", "heavy_rain", "thunderstorm"]
        is_bad_air = aqi_val >= 150
        is_storm = w_category == "thunderstorm" or wind_speed >= 45.0
        is_extreme_hot = feels_like >= 38.0

        def evaluate_activity(name: str, icon: str, good_cond: bool, warn_cond: bool, good_msg: str, warn_msg: str, bad_msg: str) -> Dict[str, Any]:
            if not good_cond and not warn_cond:
                status = "Không khuyến khích"
                color = "#E53E3E"
                desc = bad_msg
            elif warn_cond:
                status = "Cần lưu ý"
                color = "#DD6B20"
                desc = warn_msg
            else:
                status = "Rất thích hợp"
                color = "#38A169"
                desc = good_msg
            return {"name": name, "icon": icon, "status": status, "color": color, "description": desc}

        activities = [
            evaluate_activity(
                "Chạy bộ & Thể thao ngoài trời", "🏃",
                good_cond=(not is_raining and aqi_val <= 100 and 16 <= feels_like <= 32),
                warn_cond=(not is_raining and not is_storm and (100 < aqi_val <= 150 or 32 < feels_like <= 36)),
                good_msg="Thời tiết và không khí lý tưởng cho việc rèn luyện thể lực.",
                warn_msg="Chỉ nên tập luyện nhẹ nhàng vào sáng sớm hoặc chiều muộn; tránh vận động quá sức.",
                bad_msg="Không nên tập ngoài trời do mưa ướt, không khí ô nhiễm hoặc nhiệt độ quá cao."
            ),
            evaluate_activity(
                "Dã ngoại & Cắm trại (Picnic)", "🏕️",
                good_cond=(not is_raining and not is_storm and feels_like <= 32 and aqi_val <= 100),
                warn_cond=(rain_prob <= 30 and not is_storm and feels_like <= 35),
                good_msg="Trời khô ráo, không khí mát mẻ rất thích hợp dã ngoại.",
                warn_msg="Nên chuẩn bị thêm lều bạt che nắng/mưa dự phòng.",
                bad_msg="Không thích hợp dã ngoại do nguy cơ mưa dông hoặc thời tiết bất lợi."
            ),
            evaluate_activity(
                "Phơi đồ ngoài trời", "👕",
                good_cond=(not is_raining and rain_prob <= 20 and humidity <= 75 and w_category in ["clear", "mainly_clear", "partly_cloudy"]),
                warn_cond=(rain_prob <= 40 and not is_raining),
                good_msg="Nắng ráo và độ ẩm thấp giúp quần áo nhanh khô và thơm tho.",
                warn_msg="Quần áo lâu khô hơn do độ ẩm cao hoặc trời nhiều mây.",
                bad_msg="Không nên phơi đồ ngoài trời vì trời ẩm ướt hoặc có mưa làm bẩn quần áo."
            ),
            evaluate_activity(
                "Rửa xe ô tô / xe máy", "🚗",
                good_cond=(not is_raining and rain_prob <= 20 and w_category in ["clear", "mainly_clear"]),
                warn_cond=(rain_prob <= 40),
                good_msg="Thời tiết khô ráo nhiều ngày tới, rất thích hợp để rửa xe sạch sẽ.",
                warn_msg="Có xác suất mưa rải rác, xe có thể bị bẩn lại sau khi rửa.",
                bad_msg="Không nên rửa xe lúc này vì sắp có mưa hoặc đường sá đang ngập ướt."
            ),
            evaluate_activity(
                "Cà phê / Hẹn hò ngoài trời", "☕",
                good_cond=(not is_raining and not is_storm and 20 <= feels_like <= 32 and aqi_val <= 100),
                warn_cond=(not is_storm and feels_like <= 35),
                good_msg="Không gian thoáng đãng, thời tiết đẹp để ngồi quán cà phê sân vườn.",
                warn_msg="Nên chọn quán có không gian trong nhà hoặc có mái che chắn.",
                bad_msg="Nên chọn không gian kín có máy lạnh để tránh mưa dông hoặc bụi bẩn."
            )
        ]

        # -------------------------------------------------------------
        # 3. KHUYẾN NGHỊ SỨC KHỎE & AN TOÀN (HEALTH & SAFETY)
        # -------------------------------------------------------------
        health_tips = []
        if feels_like >= 35.0:
            health_tips.append("Uống từ 2 - 2.5 lít nước mỗi ngày, bổ sung oresol hoặc nước dừa để bù khoáng khi đổ mồ hôi nhiều.")
            health_tips.append("Hạn chế ở lâu trong phòng điều hòa quá lạnh rồi bước ngay ra trời nắng để tránh sốc nhiệt.")
        elif feels_like <= 15.0:
            health_tips.append("Uống nước ấm, súc miệng bằng nước muối sinh lý hàng ngày để phòng ngừa viêm họng.")
            health_tips.append("Tránh tắm gội quá muộn vào ban đêm khi nhiệt độ hạ thấp.")
        
        if humidity >= 85.0:
            health_tips.append("Độ ẩm không khí cao dễ làm sàn nhà trơn trượt; chú ý người già và trẻ nhỏ di chuyển cẩn thận.")

        if w_category == "thunderstorm":
            health_tips.append("CẢNH BÁO AN TOÀN: Khi có sấm sét, lập tức tìm nơi trú ẩn an toàn, ngắt các thiết bị điện không cần thiết và tránh đứng dưới gốc cây to.")

        if aqi_val > 100:
            health_tips.append(f"Chất lượng không khí ở mức {aqi_level}; những người có bệnh xoang, hen suyễn nên hạn chế ra đường.")

        if not health_tips:
            health_tips.append("Thời tiết ổn định, duy trì chế độ sinh hoạt và ăn uống lành mạnh hàng ngày.")

        # -------------------------------------------------------------
        # 4. GIAO THÔNG & DI CHUYỂN (COMMUTE & TRAVEL)
        # -------------------------------------------------------------
        commute_tips = []
        road_condition = "Khô ráo, tầm nhìn tốt"
        
        if w_category in ["heavy_rain", "thunderstorm"] or rain_amount >= 15.0:
            road_condition = "Đường ướt trơn trượt, nguy cơ ngập sâu và tầm nhìn giảm mạnh"
            commute_tips.append("Bật đèn xe, giảm tốc độ và giữ khoảng cách an toàn gấp đôi so với ngày thường.")
            commute_tips.append("Tránh đi vào các đoạn đường trũng thấp hoặc gần miệng cống thoát nước.")
        elif is_raining:
            road_condition = "Đường ướt, dễ trơn trượt khi phanh gấp"
            commute_tips.append("Mặc áo mưa gọn gàng (ưu tiên áo mưa bộ), tránh để tà áo quấn vào bánh xe.")
        elif w_category in ["fog"]:
            road_condition = "Sương mù hạn chế tầm nhìn"
            commute_tips.append("Bật đèn sương mù hoặc đèn chiếu gần, chú ý các khúc cua và biển báo.")

        if wind_speed >= 40.0:
            commute_tips.append(f"Gió mạnh cấp {wind_info['level']}; giữ chắc tay lái khi chạy xe máy qua cầu vượt hoặc các tòa nhà cao tầng.")

        if not commute_tips:
            commute_tips.append("Tình hình giao thông và thời tiết thuận lợi cho việc di chuyển.")

        return clean_numpy_types({
            "weather_condition": {
                "temperature": temp,
                "feels_like": feels_like,
                "weather_name": w_info["name"],
                "weather_icon": w_info["icon"],
                "rain_probability": rain_prob,
                "wind_speed": wind_speed,
                "wind_category": wind_info["name"],
                "aqi": aqi_val,
                "aqi_level": aqi_level
            },
            "clothing_recommendation": {
                "summary": clothing_summary,
                "recommended_clothes": clothing_items,
                "accessories_and_gears": accessories
            },
            "outdoor_activities": activities,
            "health_and_safety_advice": health_tips,
            "commute_and_travel": {
                "road_condition": road_condition,
                "travel_advice": commute_tips
            }
        })
