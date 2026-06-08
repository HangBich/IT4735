## Cấu trúc dự án (Project Structure)

**main.py** (Chạy giao diện chính)

**mqtt_handler.py** (Xuyên suốt việc kết nối và nhận/gửi data)

**qr_generator.py** (Tạo link ảnh VietQR)

## Module 1: Xử lý giao tiếp MQTT (mqtt_handler.py)
Đây là "bộ đàm" của hệ thống. Bạn sẽ dùng thư viện paho-mqtt (pip install paho-mqtt).

**Nhiệm vụ:**

1. Khởi tạo: Kết nối đến Broker (vd: broker.hivemq.com).

> Lắng nghe (Subscribe): Ngay khi kết nối thành công, tự động subscribe các topic: cayxang/luongxang, cayxang/ketqua, cayxang/trangthai.

> Gửi lệnh (Publish): Cung cấp một hàm (function) để UI gọi khi người dùng bấm nút "Bắt đầu", gửi chuỗi START:<số_lít> lên topic cayxang/lenh.

> Chạy ngầm: Phải sử dụng hàm client.loop_start() (chạy đa luồng) để ứng dụng không bị đơ trong lúc chờ dữ liệu từ ESP32 gửi về.

> Bắn tín hiệu (Callback): Khi nhận được data từ ESP32 (vd: số lít hiện tại hoặc chữ DONE), module này sẽ "bắn" tín hiệu sang Module UI để cập nhật màn hình.

## Module 2: Trình tạo mã thanh toán (qr_generator.py)
Module này rất ngắn gọn, không cần dùng thư viện phức tạp.

**Nhiệm vụ:**

> Nhận đầu vào là: Tổng_số_tiền (đã quy đổi từ số lít).

> Trả về một URL hình ảnh (String) theo đúng format API của VietQR.

> Công thức tham khảo: https://img.vietqr.io/image/<MÃ_NGÂN_HÀNG>-<SỐ_TÀI_KHOẢN>-compact2.jpg?amount={tong_tien}&addInfo=Thanh toan tien xang

## Module 3: Xử lý Logic cốt lõi (Core Logic)
Module này thường được viết chung trong file giao diện, đóng vai trò như não bộ của App.

**Nhiệm vụ:**

> Lưu trữ trạng thái (State): Khai báo các biến như is_pumping = False, current_liters = 0.0, price_per_liter = 25000.

> Quy đổi: Viết hàm nhỏ: Nếu người dùng nhập số tiền (vd: 50.000đ), tự động chia cho 25.000đ để ra lệnh bơm 2.0 lít. (hoặc lấy craw real data)

> Tính tiền: Khi nhận tín hiệu DONE, nhân số lít thực tế cuối cùng với đơn giá để ra số tiền cần thanh toán, sau đó gọi Module 2 để lấy mã QR.

## Module 4: Giao diện người dùng (main.py dùng Flet)
Sử dụng thư viện flet (pip install flet). Flet cho phép bạn xếp các khối (Widget) giao diện cực kỳ nhanh.

> Nhiệm vụ chia theo 3 màn hình (Views):

> Màn hình Nhập liệu (Input View):

> Một trường văn bản (TextField) để nhập số lít hoặc số tiền.

> Một nút bấm (Button) to, rõ ràng: "BẮT ĐẦU BƠM".

> Điều kiện: Nút này chỉ được phép bấm (Enable) khi ESP32 báo đang READY. Khi bấm xong, vô hiệu hóa (Disable) nút này để tránh bấm đúp.

> Màn hình Tiến trình (Progress View - Hiện lên khi đang bơm):

> Một đoạn chữ siêu to khổng lồ (Text) hiển thị số Lít đang nhảy lên liên tục.

> Một thanh tiến trình (ProgressBar) chạy theo phần trăm.

> Giao diện này sẽ liên tục nhận dữ liệu từ hàm callback của Module 1 để cập nhật số liệu.

> Màn hình Hoàn tất (Payment View):

> Ẩn thanh tiến trình đi, hiện lên dòng chữ "BƠM HOÀN TẤT!".

> Hiển thị hình ảnh (Image) load từ URL của Module 2 (Mã VietQR).

> Có một nút "Hoàn thành / Trở về trang chủ" để dọn dẹp biến, reset App chuẩn bị cho phiên bơm mới.
