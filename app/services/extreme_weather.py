import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from app.utils.calculations import clean_numpy_types, get_wind_scale


class ExtremeWeatherAnalyzer:
    """
    BE 2: Module phân tích hiện tượng bất thường & cảnh báo thời tiết nguy hiểm.
    Phát hiện nắng nóng gay gắt, đợt nắng nóng kéo dài, rét đậm rét hại, mưa lớn ngập úng,
    gió mạnh/gió bão, độ ẩm bất thường và so sánh độ lệch lịch sử.
    """

    @staticmethod
    def analyze_extremes(
        daily_data: Dict[str, list],
        historical_baseline: Optional[Dict[str, list]] = None
    ) -> Dict[str, Any]:
        if not daily_data:
            return {
                "overall_severity": "SAFE",
                "total_alerts": 0,
                "alerts": [],
                "summary": "Không có dữ liệu thời tiết để phân tích"
            }

        df = pd.DataFrame(daily_data)
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])

        alerts: List[Dict[str, Any]] = []
        severity_rank = {"SAFE": 0, "INFO": 1, "WARNING": 2, "CRITICAL": 3}
        current_max_severity = "SAFE"

        def trigger_alert(date_str: str, alert_type: str, level: str, message: str, advice: str = ""):
            nonlocal current_max_severity
            if severity_rank.get(level, 0) > severity_rank.get(current_max_severity, 0):
                current_max_severity = level
            alerts.append({
                "date": date_str,
                "type": alert_type,
                "level": level,
                "message": message,
                "advice": advice
            })

        # -------------------------------------------------------------
        # 1. PHÂN TÍCH NHIỆT ĐỘ BẤT THƯỜNG (NẮNG NÓNG, RÉT ĐẬM & BIÊN ĐỘ NHIỆT)
        # -------------------------------------------------------------
        if 'temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns:
            heatwave_counter = 0
            heatwave_start = None

            for i, row in df.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else f"Ngày {i+1}"
                t_max = float(row['temperature_2m_max'])
                t_min = float(row['temperature_2m_min'])
                amplitude = round(t_max - t_min, 1)

                # Nắng nóng gay gắt
                if t_max >= 38.0:
                    trigger_alert(
                        day_str, "NẮNG NÓNG ĐẶC BIỆT GAY GẮT", "CRITICAL",
                        f"Nhiệt độ cao nhất đạt {t_max}°C, bức xạ nhiệt cực mạnh.",
                        "Hạn chế ra đường từ 11h - 15h, uống nhiều nước, đề phòng sốc nhiệt và nguy cơ cháy nổ."
                    )
                elif t_max >= 35.0:
                    trigger_alert(
                        day_str, "NẮNG NÓNG DIỆN RỘNG", "WARNING",
                        f"Nhiệt độ cao nhất đạt {t_max}°C.",
                        "Bảo vệ da, mang áo chống nắng và bổ sung điện giải."
                    )

                # Kiểm tra chuỗi ngày nắng nóng (Heatwave)
                if t_max >= 35.0:
                    heatwave_counter += 1
                    if heatwave_start is None:
                        heatwave_start = day_str
                    if heatwave_counter >= 3 and i == len(df) - 1:
                        trigger_alert(
                            f"{heatwave_start} đến {day_str}", "ĐỢT NẮNG NÓNG KÉO DÀI (HEATWAVE)", "CRITICAL",
                            f"Nắng nóng liên tiếp {heatwave_counter} ngày (nhiệt độ >= 35°C).",
                            "Tăng cường làm mát, tiết kiệm điện vào giờ cao điểm, bảo vệ cây trồng và vật nuôi."
                        )
                else:
                    if heatwave_counter >= 3:
                        trigger_alert(
                            f"{heatwave_start} (Kéo dài {heatwave_counter} ngày)", "ĐỢT NẮNG NÓNG KÉO DÀI", "CRITICAL",
                            f"Đợt nắng nóng kéo dài {heatwave_counter} ngày liên tiếp đã diễn ra.",
                            "Chú ý bù nước và phục hồi sức khỏe."
                        )
                    heatwave_counter = 0
                    heatwave_start = None

                # Rét đậm / Rét hại
                if t_min <= 10.0:
                    trigger_alert(
                        day_str, "RÉT HẠI NGUY HIỂM", "CRITICAL",
                        f"Nhiệt độ ban đêm hạ sâu xuống {t_min}°C.",
                        "Giữ ấm cơ thể, đặc biệt cho trẻ em và người già, che chắn chuồng trại gia súc và cây trồng."
                    )
                elif t_min <= 15.0:
                    trigger_alert(
                        day_str, "RÉT ĐẬM", "WARNING",
                        f"Nhiệt độ thấp nhất giảm còn {t_min}°C.",
                        "Mặc ấm khi ra đường sáng sớm và đêm muộn."
                    )

                # Biên độ nhiệt ngày đêm lớn
                if amplitude >= 13.0:
                    trigger_alert(
                        day_str, "BIÊN ĐỘ NHIỆT LỚN", "INFO",
                        f"Chênh lệch ngày đêm lên tới {amplitude}°C (Ngày {t_max}°C - Đêm {t_min}°C).",
                        "Dễ gây cảm cúm, viêm đường hô hấp, cần điều chỉnh trang phục linh hoạt."
                    )

        # -------------------------------------------------------------
        # 2. PHÁT HIỆN MƯA LỚN & NGUY CƠ NGẬP LỤT
        # -------------------------------------------------------------
        if 'precipitation_sum' in df.columns:
            for i, row in df.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else f"Ngày {i+1}"
                rain = float(row['precipitation_sum'])

                if rain >= 70.0:
                    trigger_alert(
                        day_str, "MƯA RẤT TO & NGUY CƠ NGẬP ÚNG", "CRITICAL",
                        f"Lượng mưa cực lớn đạt {rain} mm/ngày.",
                        "Cảnh báo ngập lụt đô thị, lũ quét và sạt lở đất ở vùng núi. Hạn chế lưu thông qua khu vực ngập sâu."
                    )
                elif rain >= 30.0:
                    trigger_alert(
                        day_str, "MƯA LỚN DIỆN RỘNG", "WARNING",
                        f"Lượng mưa đạt {rain} mm/ngày.",
                        "Chú ý mang đồ đi mưa, đường trơn trượt, giảm tầm nhìn khi tham gia giao thông."
                    )

        # -------------------------------------------------------------
        # 3. PHÁT HIỆN GIÓ MẠNH / GIÓ BÃO (CHUẨN KM/H)
        # -------------------------------------------------------------
        if 'wind_speed_10m_max' in df.columns:
            for i, row in df.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else f"Ngày {i+1}"
                wind = float(row['wind_speed_10m_max'])
                wind_scale = get_wind_scale(wind)

                if wind >= 60.0:
                    trigger_alert(
                        day_str, f"GIÓ RẤT MẠNH / GIÓ BÃO (Cấp {wind_scale['level']})", "CRITICAL",
                        f"Tốc độ gió giật cực đại {wind} km/h.",
                        "Gió cấp bão nguy hiểm, đề phòng gãy đổ cây xanh, biển quảng cáo, tốc mái nhà."
                    )
                elif wind >= 39.0:
                    trigger_alert(
                        day_str, f"GIÓ KHÁ MẠNH (Cấp {wind_scale['level']})", "WARNING",
                        f"Tốc độ gió đạt {wind} km/h.",
                        "Cẩn thận khi điều khiển phương tiện trên cầu cao hoặc đường thoáng gió."
                    )

        # -------------------------------------------------------------
        # 4. PHÁT HIỆN ĐỘ ẨM BẤT THƯỜNG
        # -------------------------------------------------------------
        humidity_col = next((col for col in df.columns if 'humidity' in col), None)
        if humidity_col:
            for i, row in df.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else f"Ngày {i+1}"
                hum = float(row[humidity_col])

                if hum <= 35.0:
                    trigger_alert(
                        day_str, "KHÔ HANH BẤT THƯỜNG", "WARNING",
                        f"Độ ẩm không khí giảm mạnh xuống còn {hum}%.",
                        "Nguy cơ cao xảy ra cháy rừng và hỏa hoạn, uống đủ nước và dưỡng ẩm da."
                    )
                elif hum <= 45.0:
                    trigger_alert(
                        day_str, "KHÔ HANH", "INFO",
                        f"Độ ẩm không khí thấp {hum}%.",
                        "Bổ sung nước cho cơ thể và chú ý an toàn phòng cháy."
                    )
                elif hum >= 92.0:
                    trigger_alert(
                        day_str, "ẨM ƯỚT CAO (NỒM ẨM)", "INFO",
                        f"Độ ẩm không khí bão hòa đạt {hum}%.",
                        "Sàn nhà trơn ướt, dễ phát sinh nấm mốc và vi khuẩn. Nên bật chế độ hút ẩm điều hòa."
                    )

        # -------------------------------------------------------------
        # 5. SO SÁNH VỚI DỮ LIỆU LỊCH SỬ (BASELINE)
        # -------------------------------------------------------------
        historical_comparison = {}
        if historical_baseline and 'temperature_2m_max' in df.columns and 'temperature_2m_max' in historical_baseline:
            curr_temp_avg = float(df['temperature_2m_max'].mean())
            hist_temp_avg = float(pd.Series(historical_baseline['temperature_2m_max']).mean())
            temp_dev = round(curr_temp_avg - hist_temp_avg, 1)

            curr_rain_total = float(df['precipitation_sum'].sum()) if 'precipitation_sum' in df.columns else 0.0
            hist_rain_total = float(pd.Series(historical_baseline.get('precipitation_sum', [0])).sum())
            rain_dev = round(curr_rain_total - hist_rain_total, 1)

            if abs(temp_dev) >= 3.0:
                trigger_alert(
                    "Toàn chu kỳ", "BIẾN ĐỘNG NHIỆT ĐỘ LỚN SO VỚI QUÁ KHỨ", "WARNING",
                    f"Nhiệt độ trung bình lệch {temp_dev:+0.1f}°C so với 7 ngày trước.",
                    "Thời tiết thay đổi đột ngột giữa các tuần, cần chủ động chuẩn bị trang phục và bảo vệ sức khỏe."
                )

            historical_comparison = {
                "historical_temp_avg": round(hist_temp_avg, 1),
                "current_temp_avg": round(curr_temp_avg, 1),
                "temperature_deviation": temp_dev,
                "temperature_status": f"{'Nóng hơn' if temp_dev > 0 else 'Lạnh hơn'} {abs(temp_dev)}°C so với tuần trước",
                "historical_rain_total": round(hist_rain_total, 1),
                "current_rain_total": round(curr_rain_total, 1),
                "rain_deviation": rain_dev,
                "rain_status": f"{'Mưa nhiều hơn' if rain_dev > 0 else 'Khô ráo hơn'} {abs(rain_dev)}mm so với tuần trước"
            }

        # Tạo thông điệp tổng quan
        if current_max_severity == "CRITICAL":
            summary = "CẢNH BÁO NGUY HIỂM: Phát hiện các hiện tượng thời tiết cực đoan (nắng nóng gay gắt, mưa lũ lớn hoặc bão gió). Cần tuân thủ hướng dẫn an toàn!"
        elif current_max_severity == "WARNING":
            summary = "CẢNH BÁO THỜI TIẾT: Có hiện tượng thời tiết bất lợi diễn ra trong khu vực. Cần chú ý theo dõi và phòng ngừa."
        elif current_max_severity == "INFO":
            summary = "THỜI TIẾT ĐÁNG LƯU Ý: Thời tiết có một số biến động nhẹ về độ ẩm hoặc biên độ nhiệt nhưng không nguy hiểm."
        else:
            summary = "THỜI TIẾT AN TOÀN: Không có hiện tượng bất thường nghiêm trọng nào được ghi nhận."

        result = {
            "overall_severity": current_max_severity,
            "total_alerts": len(alerts),
            "summary": summary,
            "alerts": alerts,
            "historical_comparison": historical_comparison
        }

        return clean_numpy_types(result)