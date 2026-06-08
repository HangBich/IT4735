## PHẦN 0: GIAO ƯỚC CHUNG (CẢ HAI CÙNG PHẢI THỐNG NHẤT)
Trước khi ai về nhà nấy code, hai bạn phải chốt cứng các thông số MQTT sau, tuyệt đối không ai được tự ý đổi tên:

MQTT Broker: Dùng server nào? (Gợi ý: dùng server miễn phí broker.hivemq.com port 1883).

Topic Nhận lệnh: cayxang/lenh (Định dạng gửi: START:<số_lít>, ví dụ START:2.5).

Topic Báo trạng thái: cayxang/trangthai (Định dạng gửi: READY hoặc BUSY).

Topic Cập nhật lưu lượng: cayxang/luongxang (Định dạng gửi: số thập phân, ví dụ 0.1, 0.2...).

Topic Báo hoàn thành: cayxang/ketqua (Định dạng gửi: DONE).

Đơn giá: Chốt cứng 1 mức giá chung (vd: 25.000 VNĐ/Lít) để App tính tiền cho chuẩn.

## PHẦN 1: REQUIREMENTS CHO BẠN (LÀM APP ĐIỆN THOẠI)
Bạn là người làm giao diện tiếp xúc với khách hàng, nên App phải mượt và hiển thị thông tin chuẩn xác.

1. Giao diện (UI):

Màn hình chính: Có ô nhập số Lít muốn bơm HOẶC ô nhập số Tiền. Nếu nhập tiền, App tự động chia cho Đơn giá để ra số Lít.

Nút điều khiển: Nút "Bắt đầu bơm" (Chỉ sáng lên/bấm được khi ESP32 báo READY).

Màn hình hiển thị trong lúc bơm: Số lít và Số tiền nhảy liên tục theo thời gian thực (giống cột bơm ngoài cây xăng).

Màn hình thanh toán: Hiển thị mã QR và tổng tiền sau khi bơm xong. Có nút "Hoàn tất/Bơm cuốc mới".

2. Xử lý Logic & MQTT (UX/Tính năng):

Khi vừa mở App, tự động kết nối MQTT và Subscribe luôn 3 topics: cayxang/luongxang, cayxang/ketqua, cayxang/trangthai.

Khi bấm "Bắt đầu bơm": App Publish lệnh START:<số_lít_mục_tiêu> lên topic cayxang/lenh.

Bắt sự kiện topic cayxang/luongxang: Mỗi lần có số mới đẩy về, lấy số đó nhân với Đơn giá để hiển thị cập nhật lên màn hình.

Bắt sự kiện topic cayxang/ketqua: Thấy chữ DONE thì dừng hiệu ứng nhảy số. Lấy số lít cuối cùng tính ra Tổng Tiền.

Tạo API VietQR: Nối chuỗi URL https://img.vietqr.io/image/<Mã_Ngân_Hàng>-<Số_Tài_Khoản>-compact2.jpg?amount=<Tổng_Tiền>&addInfo=Thanh toan do xang và gán vào khung hiển thị ảnh để ra mã QR.

## PHẦN 2: REQUIREMENTS CHO BẠN KIA (LÀM ESP32 & PHẦN CỨNG)
Bạn kia sẽ đóng vai trò là "cơ bắp" của hệ thống, yêu cầu cao nhất là đếm xung phải chuẩn và không được lag.

1. Đấu nối phần cứng:

Nối Cảm biến lưu lượng (YF-S201), Module Relay (để kích máy bơm), và Nút bấm dừng khẩn cấp vào ESP32.

Đảm bảo nguồn cấp cho máy bơm (thường là 5V hoặc 12V) đủ dòng, không dùng chung nguồn điện vặt từ chân 3V3 của ESP32 để tránh sập nguồn vi điều khiển.

2. Xử lý Logic & MQTT:

Khởi động: Kết nối Wi-Fi, kết nối MQTT Broker. Subscribe topic cayxang/lenh. Publish chữ READY lên topic cayxang/trangthai để App biết là máy đã sẵn sàng.

Xử lý lệnh: Khi nhận được tin nhắn từ cayxang/lenh (ví dụ START:2.5), bóc tách chuỗi để lấy con số 2.5 lưu vào biến Target_Liters.

Bắt đầu bơm: Publish chữ BUSY lên topic cayxang/trangthai. Bật Relay cho máy bơm chạy.

Đo lường (Quan trọng): Dùng ngắt (Interrupt) để đếm xung từ cảm biến lưu lượng. Tính toán ra số lít hiện tại.

Báo cáo Realtime: Đặt một bộ đếm thời gian (dùng millis()), cứ mỗi 500ms (nửa giây) lại Publish biến số lít hiện tại lên topic cayxang/luongxang.

Tự động ngắt: Liên tục so sánh. Nếu Số lít hiện tại >= Target_Liters thì Tắt Relay ngay lập tức.

Kết thúc: Publish chữ DONE lên topic cayxang/ketqua. Chờ 3 giây rồi Publish lại chữ READY lên cayxang/trangthai để đón khách mới.

## PHẦN 3: BÍ QUYẾT TEST ĐỘC LẬP CHO HAI NGƯỜI
Hai bạn không cần phải ngồi cạnh nhau để test hệ thống. Hãy tải phần mềm MQTT Explorer (trên máy tính) về.

Lúc bạn làm App: Bạn mở App, bấm "Bắt đầu". Sau đó bạn mở MQTT Explorer lên, tự đóng vai ESP32 để Publish số liệu 0.1, 0.5, 1.0... vào topic cayxang/luongxang xem App điện thoại của bạn có nhảy số đúng không. Xong bạn Publish chữ DONE xem nó có hiện QR code không.

Lúc bạn kia làm ESP32: Cắm điện ESP32. Mở MQTT Explorer lên, tự đóng vai App điện thoại, gõ lệnh START:1.0 Publish vào topic lệnh xem máy bơm có chịu chạy và tự ngắt đúng 1 lít hay không.