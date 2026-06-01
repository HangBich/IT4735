# Humanoid Robot Digital Twin Infrastructure

Dự án xây dựng hạ tầng Bản sao kỹ thuật số (Digital Twin) thời gian thực cho Robot hình người (Humanoid Robot). Hệ thống thiết lập một trục kiến trúc khép kín từ tầng tính toán động học (Backend) qua trạm trung chuyển dữ liệu (Broker) đến giao diện hiển thị không gian ba chiều trực quan trên trình duyệt (Frontend Web UI).

---

## 1. Kiến Trúc Hệ Thống (System Architecture)

Hệ thống được thiết kế theo mô hình **Event-driven Architecture (Kiến trúc hướng sự kiện)** thông qua giao thức MQTT để đảm bảo độ trễ tối thiểu (Low Latency) và tần số cập nhật cao (~33Hz), đáp ứng điều khiển thời gian thực (Real-time Control).

* **Tầng Vật Lý / Mô Phỏng (Publisher):** Script Python điều khiển/giả lập động học toán học, tính toán tọa độ và góc xoay của từng khớp (`Bone`), phát dữ liệu qua cổng TCP `1883`.
* **Tầng Trung Chuyển (MQTT Broker):** Sử dụng *Eclipse Mosquitto*, cấu hình độc lập để mở song song cổng `1883` (TCP) và cổng `9001` (WebSockets) nhằm mục đích bắc cầu dữ liệu trực tiếp lên trình duyệt.
* **Tầng Trực Quan Hóa (Subscriber):** Ứng dụng Web Single Page (SPA) xây dựng trên nền tảng *React* + *Vite* + *Three.js*, tự động giải mã các gói tin mạng để ép hệ xương của Robot chuyển động tương ứng.

---

## 2. Công Nghệ Sử Dụng (Tech Stack)

* **Frontend UI:** React 18, Vite, Three.js, `@react-three/fiber` (React wrapper cho Three.js), `@react-three/drei` (Bộ công cụ bổ trợ 3D không gian), `mqtt.js` (MQTT WebSockets Client).
* **Middleware:** Eclipse Mosquitto Broker v2.x (Cấu hình hỗ trợ WebSockets & Anonymous access).
* **Backend / Simulation:** Python 3.x, `paho-mqtt` v2.x (Kiểm thử động học thông qua bước sóng hình sin bất đồng bộ).
* **Môi trường hệ thống:** Quản lý Runtime Node.js thông qua NVM (Node Version Manager) bảo vệ lõi hệ điều hành.

---

## 3. Cấu Trúc Thư Mục Dự Án (Project Tree)

Dự án tuân thủ cấu trúc phân tách phân hệ (Modularization) để dễ dàng tích hợp các bộ mô phỏng vật lý nặng (như MuJoCo) vào backend sau này:

```text
IT4735/DigitalTwin/
├── README.md               # Tài liệu hướng dẫn và báo cáo hệ thống
├── test_publisher.py       # Script Python giả lập tính toán động học đa khớp (Publisher)
└── web_ui/                 # Phân khu mã nguồn Frontend Dashboard (Subscriber)
    ├── package.json        # Quản lý thư viện cấu phần Node.js
    ├── public/
    │   └── models/
    │       └── humanoid.glb # Mô hình 3D Robot hình người (Rigged/Gắn hệ xương chuẩn)
    └── src/
        ├── App.jsx         # Logic lõi: Kết nối MQTT WebSockets & Render đồ họa Canvas
        └── main.jsx