# Weather Backend API

Backend FastAPI cung cấp dữ liệu thời tiết theo tên thành phố. Dự án sử dụng [Open-Meteo](https://open-meteo.com/) để tìm tọa độ, lấy thời tiết hiện tại, lịch sử 7 ngày và dự báo 7 ngày.

## Chức năng

- Tìm tọa độ thành phố bằng Open-Meteo Geocoding API.
- Lấy dữ liệu thời tiết hiện tại.
- Lấy lịch sử thời tiết 7 ngày gần nhất.
- Lấy dự báo thời tiết cho 7 ngày tiếp theo.

## Yêu cầu

- Python 3.10 trở lên.
- Git.

Phiên bản dự án này sử dụng các endpoint công khai của Open-Meteo nên **không cần API key**. Tham khảo [tài liệu Open-Meteo](https://open-meteo.com/en/docs) và [Geocoding API](https://open-meteo.com/en/docs/geocoding-api) khi cần bổ sung biến thời tiết.

## Cài đặt và chạy dự án

### 1. Clone repository

```bash
git clone https://github.com/DiTamed/weather-backend.git
cd weather-backend
```

### 2. Tạo môi trường ảo

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Cấu hình Open-Meteo

Tạo hoặc cập nhật file `.env` ở thư mục gốc dự án:

```env
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
OPEN_METEO_GEO_URL=https://geocoding-api.open-meteo.com/v1/search
```

Nếu file `.env` còn các biến `OPENWEATHER_*` cũ, hãy thay chúng bằng hai biến `OPEN_METEO_*` ở trên. Mặc dù không chứa API key, `.env` vẫn được giữ ngoài Git để mỗi môi trường có thể dùng URL cấu hình riêng.

### 5. Khởi chạy server

```bash
uvicorn app.main:app --reload
```

Server mặc định chạy tại `http://127.0.0.1:8000`.

| Địa chỉ | Mục đích |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Swagger UI để thử API |
| `http://127.0.0.1:8000/redoc` | Tài liệu API dạng ReDoc |
| `http://127.0.0.1:8000/health` | Kiểm tra server hoạt động |

## API

Mọi API thời tiết nhận query parameter `city`, ví dụ `city=Ho Chi Minh City`.

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| `GET` | `/` | Kiểm tra API đang chạy |
| `GET` | `/health` | Health check |
| `GET` | `/api/weather/current?city={city}` | Thời tiết hiện tại |
| `GET` | `/api/weather/history?city={city}` | Lịch sử 7 ngày gần nhất |
| `GET` | `/api/weather/forecast?city={city}` | Dự báo 7 ngày tiếp theo |

### Ví dụ gọi API

```bash
curl "http://127.0.0.1:8000/api/weather/current?city=Ho%20Chi%20Minh"
curl "http://127.0.0.1:8000/api/weather/history?city=Da%20Nang"
curl "http://127.0.0.1:8000/api/weather/forecast?city=Ha%20Noi"
```

Ví dụ phản hồi của API thời tiết hiện tại:

```json
{
  "success": true,
  "location": {
    "name": "Ho Chi Minh City",
    "country": "Vietnam",
    "state": "Ho Chi Minh",
    "lat": 10.8231,
    "lon": 106.6297,
    "timezone": "Asia/Ho_Chi_Minh"
  },
  "current": {
    "temperature": 30.0,
    "feels_like": 35.2,
    "humidity": 70,
    "precipitation": 0.0,
    "wind_speed": 8.1,
    "weather_code": 3
  }
}
```

Trong phản hồi `history` và `forecast`, trường `daily` chứa các mảng theo ngày: `weather_code`, nhiệt độ cao nhất/thấp nhất, tổng lượng mưa, xác suất mưa cao nhất và tốc độ gió lớn nhất. `weather_code` là mã thời tiết WMO do Open-Meteo trả về.

Nếu không tìm thấy thành phố, API trả về `404`. Lỗi khi gọi Open-Meteo hoặc lỗi cấu hình được trả về dưới dạng `500`.

## Cấu trúc dự án

```text
app/
├── api/routes/       # Khai báo các endpoint
├── services/         # Gọi Open-Meteo và xử lý dữ liệu
├── schemas/          # Các schema dữ liệu
├── config.py         # Đọc URL từ .env
└── main.py           # Khởi tạo FastAPI
data/                 # Dữ liệu của dự án
requirements.txt      # Danh sách thư viện Python
```

## Quy trình làm việc với Git

Mỗi chức năng hoặc lỗi cần sửa phải thực hiện trên một nhánh riêng; không commit trực tiếp vào `main`.

### Tạo nhánh cho công việc mới

```bash
git switch main
git pull origin main
git switch -c feature/weather-forecast
```

Quy ước đặt tên nhánh:

- `feature/ten-chuc-nang`: thêm chức năng.
- `fix/mo-ta-loi`: sửa lỗi.
- `docs/noi-dung`: cập nhật tài liệu.
- `refactor/noi-dung`: cải tổ mã nguồn.

Ví dụ: `feature/air-quality`, `fix/city-not-found`, `docs/update-readme`.

### Commit và push

Sau khi hoàn thành chức năng, kiểm tra thay đổi:

```bash
git status
git diff
```

Chỉ thêm các file liên quan, tạo commit rõ nghĩa và push nhánh:

```bash
git add app/api/routes/weather.py
git add app/services/weather_service.py
git commit -m "feat: add weather forecast endpoint"
git push -u origin feature/weather-forecast
```

`-u` chỉ cần dùng ở lần push đầu tiên. Các lần sau dùng:

```bash
git push
```

Sau khi push, tạo Pull Request từ nhánh của bạn vào `main`. Mô tả Pull Request cần nêu chức năng đã làm, cách kiểm tra và các điểm cần review.

### Đồng bộ nhánh với `main`

Trước khi tạo Pull Request, cập nhật thay đổi mới nhất từ `main`:

```bash
git fetch origin
git merge origin/main
```

Nếu có xung đột, sửa file được Git báo, sau đó hoàn tất và push lại:

```bash
git add <file-da-sua>
git commit
git push
```

