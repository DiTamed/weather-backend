# Weather Backend

Backend FastAPI cung cấp API tra cứu thời tiết hiện tại theo tên thành phố. Dữ liệu thời tiết và tọa độ được lấy từ [OpenWeather](https://openweathermap.org/api).

## Công nghệ sử dụng

- Python 3.10 trở lên
- FastAPI và Uvicorn
- httpx để gọi OpenWeather API
- python-dotenv để đọc biến môi trường

## Cấu trúc thư mục

```text
weather-backend/
├── app/
│   ├── api/routes/          # Khai báo các API endpoint
│   ├── services/            # Logic gọi dịch vụ thời tiết và địa điểm
│   ├── schemas/             # Model/schema dữ liệu (mở rộng sau này)
│   ├── config.py            # Đọc cấu hình từ .env
│   └── main.py              # Điểm khởi chạy FastAPI
├── data/                    # Dữ liệu dự án (nếu có)
├── requirements.txt         # Thư viện Python cần cài
├── .gitignore
└── README.md
```

## Thiết lập môi trường

### 1. Clone repository

```bash
git clone https://github.com/DiTamed/weather-backend.git
cd weather-backend
```

### 2. Tạo và kích hoạt môi trường ảo

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Tạo API key OpenWeather

1. Đăng ký/đăng nhập tại [OpenWeather](https://home.openweathermap.org/users/sign_up).
2. Tạo hoặc lấy API key trong mục **API keys**.
3. Tạo file `.env` ở thư mục gốc dự án.

Nội dung mẫu cho `.env`:

```env
OPENWEATHER_API_KEY=thay_api_key_cua_ban_vao_day
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
OPENWEATHER_GEO_URL=https://api.openweathermap.org/geo/1.0
```

Không commit file `.env` hoặc API key lên Git. File này đã được bỏ qua bởi `.gitignore`.

## Chạy dự án

Trong khi môi trường ảo đang được kích hoạt, chạy:

```bash
uvicorn app.main:app --reload
```

Server mặc định chạy tại `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Kiểm tra trạng thái: `http://127.0.0.1:8000/health`

## API hiện có

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| `GET` | `/` | Kiểm tra API đang chạy |
| `GET` | `/health` | Health check, trả về `{"status": "ok"}` |
| `GET` | `/api/weather/current?city={ten_thanh_pho}` | Lấy thời tiết hiện tại theo tên thành phố |

Ví dụ gọi API:

```bash
curl "http://127.0.0.1:8000/api/weather/current?city=Ho%20Chi%20Minh"
```

Ví dụ dữ liệu trả về rút gọn:

```json
{
  "success": true,
  "location": {
    "name": "Ho Chi Minh City",
    "country": "VN",
    "lat": 10.8231,
    "lon": 106.6297
  },
  "current": {
    "temperature": 30.0,
    "humidity": 70,
    "weather": "Clouds",
    "description": "mây rải rác"
  }
}
```

## Quy trình làm việc với Git

Luôn tạo nhánh mới từ `main` cho từng chức năng hoặc lỗi cần sửa. Không làm việc trực tiếp trên `main`.

### 1. Cập nhật nhánh `main`

```bash
git switch main
git pull origin main
```

### 2. Tạo nhánh mới

Quy ước đặt tên:

- `feature/ten-chuc-nang` — thêm chức năng
- `fix/mo-ta-loi` — sửa lỗi
- `docs/noi-dung` — cập nhật tài liệu
- `refactor/noi-dung` — cải tổ mã nguồn

Ví dụ thêm API dự báo:

```bash
git switch -c feature/weather-forecast
```

Kiểm tra nhánh hiện tại:

```bash
git branch --show-current
git status
```

### 3. Làm việc và kiểm tra thay đổi

Sau khi chỉnh sửa mã, chạy ứng dụng hoặc kiểm tra API trên Swagger. Sau đó xem lại các file sẽ commit:

```bash
git status
git diff
```

Không thêm `.env`, `venv/`, `__pycache__/` hoặc dữ liệu nhạy cảm vào commit.

### 4. Commit thay đổi

Chỉ add các file liên quan:

```bash
git add app/api/routes/weather.py
git add README.md
git commit -m "feat: add weather forecast endpoint"
```

Một số tiền tố commit nên dùng:

- `feat:` thêm chức năng
- `fix:` sửa lỗi
- `docs:` cập nhật tài liệu
- `refactor:` chỉnh cấu trúc nhưng không đổi hành vi
- `test:` thêm hoặc sửa kiểm thử
- `chore:` thay đổi cấu hình/công việc phụ trợ

### 5. Push nhánh lên GitHub

Lần đầu push nhánh:

```bash
git push -u origin feature/weather-forecast
```

Các lần sau trên cùng nhánh:

```bash
git push
```

Sau khi push, vào GitHub để tạo Pull Request từ nhánh của bạn vào `main`. Mô tả ngắn gọn chức năng đã làm, cách kiểm tra và các lưu ý cần review. Chỉ merge sau khi được review hoặc cả nhóm thống nhất.

### 6. Đồng bộ nhánh khi `main` có thay đổi

Trước khi tạo Pull Request hoặc khi làm việc trong thời gian dài:

```bash
git fetch origin
git merge origin/main
```

Nếu có xung đột, sửa các file được Git báo, sau đó:

```bash
git add <file-da-sua>
git commit
git push
```

## Lệnh nhanh cho một công việc mới

```bash
git switch main
git pull origin main
git switch -c feature/ten-chuc-nang
# code va kiem tra
git status
git add <cac-file-lien-quan>
git commit -m "feat: mo ta thay doi"
git push -u origin feature/ten-chuc-nang
```

