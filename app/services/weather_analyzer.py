import pandas as pd
import numpy as np
from typing import Dict, Any

class WeatherAnalyzer:
    @staticmethod
    def _clean_numpy_types(obj: Any) -> Any:
        """
        Đệ quy chuyển đổi các kiểu dữ liệu Numpy (int64, float64...) 
        về kiểu chuẩn của Python (int, float) để FastAPI có thể parse JSON.
        """
        if isinstance(obj, dict):
            return {k: WeatherAnalyzer._clean_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [WeatherAnalyzer._clean_numpy_types(v) for v in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif pd.isna(obj):
            return None
        return obj

    @staticmethod
    def analyze_daily_data(daily_data: Dict[str, list]) -> Dict[str, Any]:
        """
        Phân tích dữ liệu thời tiết thô (daily) thành các chỉ số thống kê.
        """
        if not daily_data:
            return {}

        df = pd.DataFrame(daily_data)
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])

        analysis_result = {}

        if 'temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns:
            df['temp_avg'] = (df['temperature_2m_max'] + df['temperature_2m_min']) / 2
            trend = "Tăng" if df['temp_avg'].iloc[-1] > df['temp_avg'].iloc[0] else "Giảm"
            
            analysis_result['temperature_analysis'] = {
                'avg_temp': round(df['temp_avg'].mean(), 1),
                'max_temp': round(df['temperature_2m_max'].max(), 1),
                'min_temp': round(df['temperature_2m_min'].min(), 1),
                'trend': trend
            }

        if 'precipitation_sum' in df.columns:
            rainy_days = df[df['precipitation_sum'] > 0]
            if not rainy_days.empty:
                max_rain_idx = df['precipitation_sum'].idxmax()
                max_rain_day = df.loc[max_rain_idx, 'time'].strftime('%Y-%m-%d') if 'time' in df.columns else None
            else:
                max_rain_day = None

            analysis_result['precipitation_analysis'] = {
                'total_rain': round(df['precipitation_sum'].sum(), 1),
                'avg_rain': round(df['precipitation_sum'].mean(), 1),
                'rainy_days_count': len(rainy_days),
                'max_rain_day': max_rain_day
            }

        if 'wind_speed_10m_max' in df.columns:
            analysis_result['wind_analysis'] = {
                'max_wind_speed': round(df['wind_speed_10m_max'].max(), 1),
                'avg_wind_speed': round(df['wind_speed_10m_max'].mean(), 1)
            }

        if 'apparent_temperature_max' in df.columns and 'apparent_temperature_min' in df.columns:
            analysis_result['apparent_temperature_analysis'] = {
                'max_feels_like': round(df['apparent_temperature_max'].max(), 1),
                'min_feels_like': round(df['apparent_temperature_min'].min(), 1)
            }

        humidity_col = next((col for col in df.columns if 'humidity' in col), None)
        if humidity_col:
            analysis_result['humidity_analysis'] = {
                'avg_humidity': round(df[humidity_col].mean(), 1),
                'max_humidity': round(df[humidity_col].max(), 1)
            }

        return WeatherAnalyzer._clean_numpy_types(analysis_result)

    @staticmethod
    def compare_history_vs_forecast(history_daily: Dict[str, list], forecast_daily: Dict[str, list]) -> Dict[str, Any]:
        """
        So sánh dữ liệu 7 ngày quá khứ và 7 ngày dự báo để phát hiện xu hướng thời tiết.
        """
        if not history_daily or not forecast_daily:
            return {"error": "Thiếu dữ liệu để so sánh"}

        hist_df = pd.DataFrame(history_daily)
        fore_df = pd.DataFrame(forecast_daily)

        comparison = {}

        if 'temperature_2m_max' in hist_df.columns and 'temperature_2m_max' in fore_df.columns:
            hist_avg_temp = (hist_df['temperature_2m_max'] + hist_df['temperature_2m_min']).mean() / 2
            fore_avg_temp = (fore_df['temperature_2m_max'] + fore_df['temperature_2m_min']).mean() / 2
            
            temp_diff = round(fore_avg_temp - hist_avg_temp, 1)
            comparison['temperature'] = {
                'history_avg': round(hist_avg_temp, 1),
                'forecast_avg': round(fore_avg_temp, 1),
                'difference': temp_diff,
                'trend': "Nóng lên" if temp_diff > 0.5 else ("Lạnh đi" if temp_diff < -0.5 else "Bình thường")
            }

        if 'precipitation_sum' in hist_df.columns and 'precipitation_sum' in fore_df.columns:
            hist_rain = hist_df['precipitation_sum'].sum()
            fore_rain = fore_df['precipitation_sum'].sum()
            
            comparison['precipitation'] = {
                'history_total': round(hist_rain, 1),
                'forecast_total': round(fore_rain, 1),
                'trend': "Nhiều mưa hơn" if fore_rain > hist_rain else "Ít mưa hơn"
            }

        return WeatherAnalyzer._clean_numpy_types(comparison)