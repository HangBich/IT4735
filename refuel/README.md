# Dự án đổ xăng

Luồng:

Quá trình bơm xăng sẽ diễn ra theo dòng thời gian (Timeline) sau:

1. Khởi động: * ESP32 kết nối Wi-Fi, sau đó kết nối với MQTT Broker.

    > ESP32 Subscribe (lắng nghe) topic cayxang/lenh.

2. App ra lệnh: * Người dùng chọn bơm 2 lít trên App.

    > App Publish chuỗi START:2.0 vào topic cayxang/lenh.

3. ESP32 nhận lệnh & Bơm:

    > Ngay lập tức (độ trễ tính bằng mili-giây), hàm callback của MQTT trên ESP32 bắt được chữ START:2.0.

    > ESP32 bật Relay bơm.

    > Khi cảm biến lưu lượng đếm xung, cứ mỗi lần được thêm 0.1 lít, ESP32 lại Publish con số này lên topic cayxang/luongxang.

    > Điện thoại của khách hàng (đang Subscribe topic cayxang/luongxang) sẽ nhận được số liệu và màn hình tự động nhảy số tiền/số lít y hệt trụ bơm ngoài đời.

4. Hoàn thành:

    > Khi đủ 2 lít, ESP32 tắt Relay.

    > ESP32 Publish tín hiệu DONE lên topic cayxang/ketqua.

    > App nhận được chữ DONE, lập tức tắt thanh tiến trình bơm, tính tổng tiền và gọi API VietQR để hiện ảnh quét mã thanh toán.

## TÀI LIỆU FRONTEND

https://docs.google.com/document/d/1M_GNZfm3kO8VNdyE1TfxBXfLq4xpuQ5O2cTcudJACpE/edit?usp=sharing
