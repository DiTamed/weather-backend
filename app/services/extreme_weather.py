import pandas as pd
import numpy as np
from typing import Dict, Any

class ExtremeWeatherAnalyzer:
    @staticmethod
    def _clean_numpy_types(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: ExtremeWeatherAnalyzer._clean_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ExtremeWeatherAnalyzer._clean_numpy_types(v) for v in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif pd.isna(obj):
            return None
        return obj

    @staticmethod
    def analyze_extremes(daily_data: Dict[str, list], historical_baseline: Dict[str, list] = None) -> Dict[str, Any]:
        if not daily_data:
            return {"alerts": [], "summary": "Không có dữ liệu"}

        df = pd.DataFrame(daily_data)
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])

        alerts = []
        severity_levels = {"INFO": 1, "WARNING": 2, "CRITICAL": 3}
        max_severity = "INFO"

        def update_severity(level):
            nonlocal max_severity
            if severity_levels[level] > severity_levels[max_severity]:
                max_severity = level

        # 1. Phát hiện Nhiệt độ bất thường (Nắng nóng & Rét đậm)
        if 'temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns:
            for _, row in df.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else "N/A"
                t_max = row['temperature_2m_max']
                t_min = row['temperature_2m_min']
                
                if t_max >= 35.0:
                    level = "CRITICAL" if t_max >= 38.0 else "WARNING"
                    update_severity(level)
                    alerts.append({"date": day_str, "type": "NẮNG NÓNG", "level": level, "message": f"Nhiệt độ cao đạt {t_max}°C"})
                
                if t_min <= 15.0:
                    level = "CRITICAL" if t_min <= 10.0 else "WARNING"
                    update_severity(level)
                    alerts.append({"date": day_str, "type": "RÉT ĐẬM", "level": level, "message": f"Nhiệt độ thấp giảm còn {t_min}°C"})

        # 2. Phát hiện Mưa lớn
        if 'precipitation_sum' in df.columns:
            heavy_rain_days = df[df['precipitation_sum'] >= 30.0]
            for _, row in heavy_rain_days.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else "N/A"
                rain = row['precipitation_sum']
                level = "CRITICAL" if rain >= 70.0 else "WARNING"
                update_severity(level)
                alerts.append({"date": day_str, "type": "MƯA LỚN", "level": level, "message": f"Lượng mưa đạt {rain}mm"})

        # 3. Phát hiện Gió mạnh
        if 'wind_speed_10m_max' in df.columns:
            strong_wind_days = df[df['wind_speed_10m_max'] >= 15.0]
            for _, row in strong_wind_days.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else "N/A"
                wind = row['wind_speed_10m_max']
                level = "CRITICAL" if wind >= 20.0 else "WARNING"
                update_severity(level)
                alerts.append({"date": day_str, "type": "GIÓ MẠNH", "level": level, "message": f"Gió giật mức {wind} m/s"})

        # 4. Phát hiện Độ ẩm bất thường
        humidity_col = next((col for col in df.columns if 'humidity' in col), None)
        if humidity_col:
            extreme_hum = df[(df[humidity_col] <= 40) | (df[humidity_col] >= 90)]
            for _, row in extreme_hum.iterrows():
                day_str = row['time'].strftime('%Y-%m-%d') if 'time' in df.columns else "N/A"
                hum = row[humidity_col]
                h_type = "KHÔ HANH" if hum <= 40 else "ẨM ƯỚT CAO"
                alerts.append({"date": day_str, "type": h_type, "level": "INFO", "message": f"Độ ẩm ở mức {hum}%"})

        # 5. So sánh với lịch sử
        historical_comparison = {}
        if historical_baseline and 'temperature_2m_max' in df.columns and 'temperature_2m_max' in historical_baseline:
            current_avg = df['temperature_2m_max'].mean()
            hist_avg = pd.Series(historical_baseline['temperature_2m_max']).mean()
            diff = round(current_avg - hist_avg, 1)
            historical_comparison = {
                "historical_avg": round(hist_avg, 1),
                "current_avg": round(current_avg, 1),
                "deviation": diff,
                "status": "Nóng hơn tuần trước" if diff > 0 else "Lạnh hơn tuần trước"
            }

        result = {
            "overall_severity": max_severity,
            "total_alerts": len(alerts),
            "alerts": alerts,
            "historical_comparison": historical_comparison
        }

        return ExtremeWeatherAnalyzer._clean_numpy_types(result)