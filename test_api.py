import asyncio
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from app.main import app

def test_endpoints():
    client = TestClient(app)
    
    cities = ["Ho Chi Minh", "Ha Noi", "Da Lat"]
    
    print("=" * 60)
    print("BẮT ĐẦU KIỂM TRA HỆ THỐNG API (BE1, BE2, BE3)")
    print("=" * 60)
    
    # 1. Health check & Root
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root failed: {r_root.status_code}"
    print("[PASS] GET / ->", r_root.json()["message"])

    r_health = client.get("/health")
    assert r_health.status_code == 200
    print("[PASS] GET /health -> status ok")

    for city in cities:
        print("\n" + "-" * 50)
        print(f"KIỂM TRA VỚI THÀNH PHỐ: {city}")
        print("-" * 50)

        # BE1: Current Weather
        r_curr = client.get(f"/api/weather/current?city={city}")
        assert r_curr.status_code == 200, f"Current weather failed for {city}: {r_curr.text}"
        curr_data = r_curr.json()
        print(f"[PASS] BE1 /api/weather/current -> Temp: {curr_data['current']['temperature']}°C, Feels like: {curr_data['current']['feels_like']}°C")

        # BE1: 15-days Weather
        r_15d = client.get(f"/api/weather/15-days?city={city}")
        assert r_15d.status_code == 200, f"15 days failed: {r_15d.text}"
        days_data = r_15d.json()
        print(f"[PASS] BE1 /api/weather/15-days -> Total days: {len(days_data['daily'])}, Temp Avg: {days_data['analysis']['temperature_analysis']['avg_temp']}°C, Trend: {days_data['analysis']['temperature_analysis']['trend']}")

        # BE1: Analysis Summary
        r_sum = client.get(f"/api/analysis/summary?city={city}")
        assert r_sum.status_code == 200, f"Analysis summary failed: {r_sum.text}"
        sum_data = r_sum.json()
        print(f"[PASS] BE1 /api/analysis/summary -> Rain: {sum_data['analysis']['precipitation_analysis']['total_rain']}mm, Rainy days: {sum_data['analysis']['precipitation_analysis']['rainy_days_count']}")

        # BE1: Trends
        r_trend = client.get(f"/api/analysis/trends?city={city}")
        assert r_trend.status_code == 200, f"Trends failed: {r_trend.text}"
        print(f"[PASS] BE1 /api/analysis/trends -> Summary: {r_trend.json()['trend_comparison'].get('overall_trend_summary')}")

        # BE2: Extreme Weather & Alerts
        r_ext = client.get(f"/api/analysis/extremes?city={city}")
        assert r_ext.status_code == 200, f"Extremes failed: {r_ext.text}"
        ext_data = r_ext.json()
        print(f"[PASS] BE2 /api/analysis/extremes -> Severity: {ext_data['overall_severity']}, Alerts count: {ext_data['total_alerts']}")

        # BE3: Air Quality (AQI)
        r_aq = client.get(f"/api/recommendations/air-quality?city={city}")
        assert r_aq.status_code == 200, f"Air quality failed: {r_aq.text}"
        aq_data = r_aq.json()["air_quality"]
        print(f"[PASS] BE3 /api/recommendations/air-quality -> AQI: {aq_data['aqi']} ({aq_data['level']}), Dominant: {aq_data['dominant_pollutant']}")

        # BE3: Lifestyle Recommendations
        r_life = client.get(f"/api/recommendations/lifestyle?city={city}")
        assert r_life.status_code == 200, f"Lifestyle failed: {r_life.text}"
        life_data = r_life.json()["lifestyle_recommendations"]
        print(f"[PASS] BE3 /api/recommendations/lifestyle -> Clothing: {life_data['clothing_recommendation']['summary']}")

        # BE3: Smart Agriculture (Rule-Based + ML)
        r_agri = client.get(f"/api/recommendations/agriculture?city={city}")
        assert r_agri.status_code == 200, f"Agriculture failed: {r_agri.text}"
        agri_data = r_agri.json()["agriculture_recommendations"]
        top_crops = [f"{c['name']} ({c['suitability_score']}%)" for c in agri_data["top_recommended_crops"][:3]]
        print(f"[PASS] BE3 /api/recommendations/agriculture -> Region: {agri_data['location_info']['region']}, Season: {agri_data['location_info']['current_season']}")
        print(f"       Top Crops: {', '.join(top_crops)}")

        # BE3: Overview
        r_ov = client.get(f"/api/recommendations/overview?city={city}")
        assert r_ov.status_code == 200, f"Overview failed: {r_ov.text}"
        print(f"[PASS] BE3 /api/recommendations/overview -> Successfully fetched all modules for {city}")

    print("\n" + "=" * 60)
    print("TẤT CẢ CÁC BÀI KIỂM TRA ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
