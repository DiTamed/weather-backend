import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from app.utils.calculations import clean_numpy_types, get_wind_scale


class WeatherAnalyzer:
    """
    BE 1: Module phân tích dữ liệu thời tiết (Pandas-powered).
    Biến dữ liệu thô thành các chỉ số thống kê, xu hướng và so sánh quá khứ/dự báo.
    """

    @staticmethod
    def analyze_daily_data(daily_data: Dict[str, list]) -> Dict[str, Any]:
        """
        Phân tích dữ liệu thời tiết thô (daily) thành các chỉ số thống kê hoàn chỉnh.
        """
        if not daily_data:
            return {}

        df = pd.DataFrame(daily_data)
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])

        analysis_result = {}

        # 1. Phân tích nhiệt độ & Cảm giác nhiệt
        if 'temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns:
            df['temp_avg'] = (df['temperature_2m_max'] + df['temperature_2m_min']) / 2
            
            first_temp = df['temp_avg'].iloc[0]
            last_temp = df['temp_avg'].iloc[-1]
            temp_diff = round(last_temp - first_temp, 1)
            
            if temp_diff > 1.0:
                trend = "Tăng"
            elif temp_diff < -1.0:
                trend = "Giảm"
            else:
                trend = "Ổn định"

            analysis_result['temperature_analysis'] = {
                'avg_temp': round(float(df['temp_avg'].mean()), 1),
                'max_temp': round(float(df['temperature_2m_max'].max()), 1),
                'min_temp': round(float(df['temperature_2m_min'].min()), 1),
                'temp_amplitude_avg': round(float((df['temperature_2m_max'] - df['temperature_2m_min']).mean()), 1),
                'trend': trend,
                'trend_description': f"Nhiệt độ có xu hướng {trend.lower()} ({'+' if temp_diff > 0 else ''}{temp_diff}°C so với đầu kỳ)"
            }

        # Cảm giác nhiệt (Apparent temperature)
        if 'apparent_temperature_max' in df.columns and 'apparent_temperature_min' in df.columns:
            apparent_avg = (df['apparent_temperature_max'] + df['apparent_temperature_min']) / 2
            analysis_result['apparent_temperature_analysis'] = {
                'avg_feels_like': round(float(apparent_avg.mean()), 1),
                'max_feels_like': round(float(df['apparent_temperature_max'].max()), 1),
                'min_feels_like': round(float(df['apparent_temperature_min'].min()), 1)
            }

        # 2. Phân tích lượng mưa
        if 'precipitation_sum' in df.columns:
            rainy_days = df[df['precipitation_sum'] > 0.1]
            total_rain = round(float(df['precipitation_sum'].sum()), 1)
            avg_rain = round(float(df['precipitation_sum'].mean()), 1)
            rainy_days_count = len(rainy_days)
            
            if not rainy_days.empty:
                max_rain_idx = df['precipitation_sum'].idxmax()
                max_rain_day = df.loc[max_rain_idx, 'time'].strftime('%Y-%m-%d') if 'time' in df.columns else None
                max_rain_amount = round(float(df.loc[max_rain_idx, 'precipitation_sum']), 1)
            else:
                max_rain_day = None
                max_rain_amount = 0.0

            analysis_result['precipitation_analysis'] = {
                'total_rain': total_rain,
                'avg_rain': avg_rain,
                'rainy_days_count': rainy_days_count,
                'rainy_days_ratio': round(rainy_days_count / len(df) * 100, 1) if len(df) > 0 else 0,
                'max_rain_day': max_rain_day,
                'max_rain_amount': max_rain_amount,
                'rain_evaluation': "Nhiều mưa" if total_rain >= 50 else ("Mưa vừa" if total_rain >= 15 else "Ít mưa / Khô ráo")
            }

        # 3. Phân tích tốc độ gió
        if 'wind_speed_10m_max' in df.columns:
            max_wind = round(float(df['wind_speed_10m_max'].max()), 1)
            avg_wind = round(float(df['wind_speed_10m_max'].mean()), 1)
            min_wind = round(float(df['wind_speed_10m_max'].min()), 1)
            wind_scale = get_wind_scale(max_wind)
            
            analysis_result['wind_analysis'] = {
                'max_wind_speed': max_wind,
                'avg_wind_speed': avg_wind,
                'min_wind_speed': min_wind,
                'wind_scale_level': wind_scale['level'],
                'wind_category': wind_scale['name'],
                'unit': 'km/h'
            }

        # 4. Phân tích độ ẩm
        humidity_col = next((col for col in df.columns if 'humidity' in col), None)
        if humidity_col:
            avg_hum = round(float(df[humidity_col].mean()), 1)
            max_hum = round(float(df[humidity_col].max()), 1)
            min_hum = round(float(df[humidity_col].min()), 1)
            
            analysis_result['humidity_analysis'] = {
                'avg_humidity': avg_hum,
                'max_humidity': max_hum,
                'min_humidity': min_hum,
                'evaluation': "Độ ẩm cao (ẩm ướt)" if avg_hum >= 80 else ("Khô hanh" if avg_hum <= 50 else "Độ ẩm dễ chịu")
            }

        return clean_numpy_types(analysis_result)

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
        summary_sentences = []

        # 1. So sánh nhiệt độ
        if 'temperature_2m_max' in hist_df.columns and 'temperature_2m_max' in fore_df.columns:
            hist_avg_temp = float((hist_df['temperature_2m_max'] + hist_df['temperature_2m_min']).mean() / 2)
            fore_avg_temp = float((fore_df['temperature_2m_max'] + fore_df['temperature_2m_min']).mean() / 2)
            
            temp_diff = round(fore_avg_temp - hist_avg_temp, 1)
            if temp_diff > 0.5:
                temp_trend = "Nóng lên"
            elif temp_diff < -0.5:
                temp_trend = "Lạnh đi"
            else:
                temp_trend = "Ổn định"

            comparison['temperature'] = {
                'history_avg': round(hist_avg_temp, 1),
                'forecast_avg': round(fore_avg_temp, 1),
                'difference': temp_diff,
                'trend': temp_trend
            }
            summary_sentences.append(f"Dự báo 7 ngày tới có xu hướng {temp_trend.lower()} ({'+' if temp_diff > 0 else ''}{temp_diff}°C so với tuần trước)")

        # 2. So sánh lượng mưa
        if 'precipitation_sum' in hist_df.columns and 'precipitation_sum' in fore_df.columns:
            hist_rain = float(hist_df['precipitation_sum'].sum())
            fore_rain = float(fore_df['precipitation_sum'].sum())
            rain_diff = round(fore_rain - hist_rain, 1)
            
            if rain_diff > 5.0:
                rain_trend = "Nhiều mưa hơn rõ rệt"
            elif rain_diff < -5.0:
                rain_trend = "Khô ráo hơn, giảm mưa"
            else:
                rain_trend = "Lượng mưa tương đương"

            comparison['precipitation'] = {
                'history_total': round(hist_rain, 1),
                'forecast_total': round(fore_rain, 1),
                'difference': rain_diff,
                'trend': rain_trend
            }
            summary_sentences.append(f"Lượng mưa dự báo {rain_trend.lower()} ({fore_rain:.1f}mm so với {hist_rain:.1f}mm tuần trước)")

        # 3. So sánh độ ẩm
        hist_hum_col = next((col for col in hist_df.columns if 'humidity' in col), None)
        fore_hum_col = next((col for col in fore_df.columns if 'humidity' in col), None)
        if hist_hum_col and fore_hum_col:
            hist_hum = float(hist_df[hist_hum_col].mean())
            fore_hum = float(fore_df[fore_hum_col].mean())
            hum_diff = round(fore_hum - hist_hum, 1)
            
            comparison['humidity'] = {
                'history_avg': round(hist_hum, 1),
                'forecast_avg': round(fore_hum, 1),
                'difference': hum_diff,
                'trend': "Ẩm hơn" if hum_diff > 3 else ("Khô hơn" if hum_diff < -3 else "Không đổi nhiều")
            }

        # 4. So sánh gió
        if 'wind_speed_10m_max' in hist_df.columns and 'wind_speed_10m_max' in fore_df.columns:
            hist_wind = float(hist_df['wind_speed_10m_max'].mean())
            fore_wind = float(fore_df['wind_speed_10m_max'].mean())
            wind_diff = round(fore_wind - hist_wind, 1)

            comparison['wind'] = {
                'history_avg_speed': round(hist_wind, 1),
                'forecast_avg_speed': round(fore_wind, 1),
                'difference': wind_diff,
                'trend': "Gió mạnh hơn" if wind_diff > 3 else ("Gió dịu hơn" if wind_diff < -3 else "Ổn định")
            }

        comparison['overall_trend_summary'] = ". ".join(summary_sentences) + "." if summary_sentences else "Dữ liệu thời tiết duy trì ổn định."

        return clean_numpy_types(comparison)