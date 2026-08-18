# Weather Backend API & Intelligent Recommendation System

Backend FastAPI cung cấp dịch vụ thời tiết, phân tích số liệu nâng cao, phát hiện hiện tượng bất thường và đưa ra các khuyến nghị thông minh (Nông nghiệp thông minh, Gợi ý sinh hoạt, Phân tích chất lượng không khí AQI).

Hệ thống sử dụng dữ liệu từ [Open-Meteo Weather Forecast API](https://open-meteo.com/) và [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) (hoàn toàn miễn phí, không yêu cầu API key).

---

## Các Module Chức Năng

### 1. BE 1 — Phân tích dữ liệu thời tiết (Weather Analytics)
- Thu thập dữ liệu thời tiết từ Open-Meteo.
- Xử lý, làm sạch và chuẩn hóa dữ liệu bằng **Pandas** và **NumPy**.
- **Phân tích nhiệt độ**: Nhiệt độ trung bình, cao nhất, thấp nhất, biên độ nhiệt, cảm giác nhiệt thực tế (`feels_like`) và xu hướng tăng/giảm.
- **Phân tích lượng mưa**: Tổng lượng mưa, lượng mưa trung bình, số ngày có mưa, tỷ lệ ngày mưa, ngày có mưa lớn nhất.
- **Phân tích độ ẩm**: Độ ẩm trung bình, cao nhất, thấp nhất và đánh giá trạng thái ẩm ướt/khô hanh.
- **Phân tích tốc độ gió**: Tốc độ gió cực đại, trung bình và phân loại cấp gió theo thang Beaufort.
- **So sánh 15 ngày**: Đối chiếu 7 ngày lịch sử với 7 ngày dự báo tương lai để phát hiện xu hướng biến đổi khí hậu ngắn hạn.

### 2. BE 2 — Phân tích bất thường & Cảnh báo thời tiết (Extreme Weather Alerts)
- **Module `extreme_weather.py`**:
  - Phát hiện nắng nóng gay gắt ($\ge 35^\circ\text{C}$, $\ge 38^\circ\text{C}$) và đợt nắng nóng kéo dài (Heatwave $\ge 3$ ngày liên tiếp).
  - Phát hiện rét đậm, rét hại nguy hiểm ($\le 15^\circ\text{C}$, $\le 10^\circ\text{C}$).
  - Cảnh báo mưa to, mưa rất to ($\ge 30\text{mm}$, $\ge 70\text{mm}$) và nguy cơ ngập lụt, sạt lở.
  - Cảnh báo gió mạnh, gió bão chuẩn hóa theo $\text{km/h}$.
  - Cảnh báo độ ẩm bất thường (khô hanh $\le 35\%$ nguy cơ cháy nổ, nồm ẩm $\ge 92\%$).
  - Phân cấp mức độ nguy hiểm: `SAFE` $\rightarrow$ `INFO` $\rightarrow$ `WARNING` $\rightarrow$ `CRITICAL`.
  - So sánh độ lệch nhiệt độ và lượng mưa với dữ liệu lịch sử tuần trước.

### 3. BE 3 — Phân tích thông minh & Recommendation
- **Trụ cột 1: Nông nghiệp thông minh (Smart Agriculture)**:
  - Phân tích nhiệt độ, lượng mưa, độ ẩm, mùa vụ (Xuân/Hạ/Thu/Đông hoặc Mùa Mưa/Mùa Khô) và vùng sinh thái nông nghiệp Việt Nam (Bắc Bộ, Trung Bộ, Tây Nguyên, Nam Bộ).
  - Kết hợp hệ thống tri thức nông học **Rule-Based Engine** và mô hình học máy **Machine Learning (Random Forest Classifier)**.
  - Đề xuất cây trồng tối ưu kèm điểm tương thích (Suitability Score $0-100\%$).
  - Hướng dẫn chế độ tưới tiêu, thoát nước và cảnh báo rủi ro sâu bệnh (đạo ôn, rầy nâu, thán thư, mốc sương).
- **Trụ cột 2: Gợi ý sinh hoạt đời sống (Daily Life Recommendations)**:
  - Khuyến nghị trang phục linh hoạt theo cảm giác nhiệt và phụ kiện đi kèm (ô dù, áo mưa, kem chống nắng, kính râm, khẩu trang N95).
  - Đánh giá tính khả thi cho các hoạt động ngoài trời: Thể thao / Chạy bộ, Dã ngoại / Cắm trại, Phơi đồ, Rửa xe, Cà phê sân vườn.
  - Lời khuyên sức khỏe, phòng chống sốc nhiệt, bảo vệ đường hô hấp và an toàn sấm sét.
  - Cảnh báo giao thông, đường trơn trượt và ngập nước.
- **Trụ cột 3: Phân tích chất lượng không khí (Air Quality - AQI)**:
  - Tích hợp Open-Meteo Air Quality API với các thông số: $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{CO}$, $\text{NO}_2$, $\text{O}_3$, $\text{SO}_2$.
  - Tính toán Sub-index và chỉ số AQI tổng hợp theo chuẩn EPA.
  - Xác định chất gây ô nhiễm chủ đạo (Dominant Pollutant).
  - Đưa ra khuyến nghị sức khỏe cho cộng đồng và nhóm người nhạy cảm (trẻ nhỏ, người già, người mắc bệnh hô hấp/tim mạch).

---

## Cài đặt và Chạy

### 1. Kích hoạt môi trường ảo
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Khởi chạy Server
```bash
uvicorn app.main:app --reload
```

Swagger UI thử nghiệm API tại: `http://127.0.0.1:8000/docs`

---

## Danh sách API Endpoints

### Thời tiết & Dự báo (Weather)
| Method | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/api/weather/current?city={city}` | Lấy thời tiết hiện tại |
| `GET` | `/api/weather/15-days?city={city}` | Lấy dữ liệu 15 ngày (kèm phân tích BE1) |
| `GET` | `/api/weather/alerts?city={city}` | Cảnh báo thời tiết bất thường |

### Phân tích số liệu (Analysis - BE 1 & BE 2)
| Method | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/api/analysis/summary?city={city}` | Báo cáo thống kê toàn diện thời tiết (Nhiệt độ, Mưa, Gió, Độ ẩm) |
| `GET` | `/api/analysis/trends?city={city}` | So sánh xu hướng 7 ngày quá khứ vs 7 ngày tương lai |
| `GET` | `/api/analysis/extremes?city={city}` | Phát hiện hiện tượng cực đoan và phân cấp cảnh báo nguy hiểm |

### Khuyến nghị thông minh (Smart Recommendations - BE 3)
| Method | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/api/recommendations/lifestyle?city={city}` | Gợi ý trang phục, ngoài trời, sức khỏe và giao thông |
| `GET` | `/api/recommendations/agriculture?city={city}` | Đề xuất cây trồng Rule-Based + Machine Learning & tưới tiêu |
| `GET` | `/api/recommendations/air-quality?city={city}` | Phân tích nồng độ ô nhiễm, AQI và khuyến nghị y tế |
| `GET` | `/api/recommendations/overview?city={city}` | Tổng hợp thông minh toàn bộ chỉ số thời tiết, AQI & khuyến nghị |
