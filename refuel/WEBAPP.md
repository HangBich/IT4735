## Cấu trúc thư mục cho Docker

Bạn tạo một thư mục chứa App, bên trong sắp xếp gọn gàng như sau:

**main.py** (Chứa giao diện Flet và logic)

**mqtt_handler.py** (Xử lý kết nối ESP32)

**qr_generator.py** (Tạo link VietQR)

**requirements.txt** (Khai báo thư viện: flet, paho-mqtt)

Dockerfile (Bản thiết kế để Docker nhốt app của bạn vào container)

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["flet", "run", "--web", "--port", "8000", "--host", "0.0.0.0", "main.py"]

> docker build -t app-cay-xang .

> docker run -p 8000:8000 app-cay-xang


## Con đường 1: "Đào hầm" bằng Ngrok (Nhanh nhất để Demo, báo cáo)
Đây là cách các sinh viên thường dùng nhất khi muốn show project cho thầy cô xem mà không có thời gian setup server rườm rà.

Cách làm: Bạn tải một phần mềm miễn phí tên là Ngrok về laptop. Cứ bật Docker cho Web App chạy ở cổng 8000 bình thường, sau đó gõ thêm một lệnh trên terminal: ngrok http 8000.

Kết quả: Ngrok sẽ lập tức tạo ra một đường hầm ảo và cấp cho bạn một cái link cực kỳ xịn xò, ví dụ: https://cayxang123.ngrok-free.app.

Sử dụng: Bạn gửi link này cho bất kỳ ai, họ dùng 4G hay Wi-Fi ở Mỹ cũng truy cập được vào Web App trên máy bạn.

Điểm yếu: Nó phụ thuộc vào cái laptop của bạn. Nếu bạn gập máy tính lại hoặc tắt Ngrok, đường link kia sẽ "chết" ngay lập tức.

## Con đường 2: Đẩy lên Cloud
Nếu bạn muốn Web App này sống 24/7, hoạt động độc lập mà không cần bật máy tính cá nhân.

Cách làm: Bạn mang nguyên cái thư mục chứa file Dockerfile đẩy lên các dịch vụ cho thuê Server Cloud miễn phí (gợi ý: Render.com hoặc Koyeb). Các hệ thống này rất thông minh, nó tự đọc file Docker của bạn, tự xây dựng môi trường ảo và tự chạy đoạn code Flet.

Kết quả: Họ cấp cho bạn một tên miền vĩnh viễn (VD: https://trambom-bachkhoa.onrender.com).

Điểm mạnh: Chuyên nghiệp, ổn định, giống hệt cách các công ty công nghệ phát hành sản phẩm. Đem link này nhúng vào slide báo cáo thì điểm tối đa.


## TÓM LẠI: ESP32 (bắt Wi-Fi trạm) -> Gửi data lên -> HiveMQ (Server trung gian) <- Lấy data về <- Web App (chạy trên 4G).
