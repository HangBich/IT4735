# 🤖 Digital Twin for Humanoid Robot via MQTT

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-Three.js-61DAFB.svg)
![MQTT](https://img.shields.io/badge/Protocol-MQTT%20%7C%20WebSockets-orange.svg)

## 📌 Tổng quan dự án (Project Overview)

Dự án này xây dựng một **Bản sao kỹ thuật số (Digital Twin)** thời gian thực cho hệ thống Robot hình người (Humanoid Robot). Hệ thống giải quyết bài toán cốt lõi trong Internet of Things (IoT) và Robotics: Thu thập dữ liệu động học (Kinematics Data Ingestion) ở tần số cao từ kiến trúc viễn biên phân tán và đồng bộ hóa trạng thái vật lý vào môi trường không gian ảo 3D. 

Dự án được phát triển trong khuôn khổ học phần **IoT và Ứng dụng (IT4735)**, hướng tới việc tạo tiền đề cho các nghiên cứu về trí tuệ nhân tạo vật lý (Physical AI) và mô phỏng học tăng cường (Reinforcement Learning).

## 🏗 Kiến trúc hệ thống (System Architecture)

Hệ thống hoạt động dựa trên mô hình **Pub/Sub** với 3 phân hệ chính:

1. **Edge Layer (Python Simulation):** Mô phỏng vi điều khiển tại các khớp (Joints) của robot. Đóng vai trò là các Publishers liên tục sinh ra dữ liệu góc quay (Joint Angles) theo các quỹ đạo toán học và đẩy lên Broker.
2. **Network Layer (Mosquitto Broker):** Trạm trung chuyển dữ liệu trung tâm. Cấu hình hỗ trợ đồng thời TCP (cho thiết bị viễn biên) và WebSockets (cho trình duyệt Web). Sử dụng cơ chế `Retained Messages` để đảm bảo tính nhất quán trạng thái.
3. **Application Layer (React + Three.js):** Giao diện Web 3D thời gian thực. Đóng vai trò là Subscriber, sử dụng `Wildcard Topics` để lắng nghe toàn bộ mạng lưới và render chuyển động của robot ở mức độ mượt mà (60 FPS).

## AIM
**input**: Một luồng dữ liệu số liên tục đại diện cho góc quay (radian) của các khớp động cơ trên cơ thể robot. Trong đồ án này, bạn không cần mua phần cứng vội. Đầu vào sẽ là một file script Python do bạn tự viết, sử dụng các hàm toán học (như sóng hình sin) để liên tục sinh ra các con số góc quay cho khủy tay, đầu gối, khớp háng... và đẩy lên mạng MQTT.

**output**: Một màn hình trình duyệt Web hiển thị mô hình 3D của robot. Khi script Python chạy và thay đổi các con số radian ở đầu vào, mô hình 3D trên web phải lập tức cử động các khớp tương ứng một cách mượt mà, đồng bộ theo thời gian thực với độ trễ tối thiểu.

## SKILLS REQUIRED

+ Python (backend/edge): Xây dựng luồng xử lý dữ liệu (Multi-threading), đóng gói Payload (JSON hoặc Protobuf), và sử dụng thư viện MQTT (paho-mqtt) để kết nối.

+ Networking: Nắm vững cách thiết lập Mosquitto Broker. Quan trọng nhất là hiểu cách mở cổng WebSockets, vì trình duyệt web không thể giao tiếp trực tiếp bằng giao thức TCP thuần túy của IoT.

+ Frontend (3D): Nền tảng về JavaScript/React và sử dụng thư viện Three.js (hoặc React Three Fiber). Parse file thiết kế cơ khí 3D chuẩn (.urdf hoặc .gltf) và render nó lên web.

## ROADMAP 
1. **Frontend:** Tải một mô hình mã nguồn mở của Humanoid (ví dụ file URDF của robot Nao hoặc Atlas). Dựng một trang web React đơn giản load được mô hình này lên màn hình để thấy nó đứng yên trước. Không cần quan tâm đến dữ liệu vội.

Xong chặng 1

2. **MQTT Broker:** Cài đặt Mosquitto trên máy tính. Sửa file cấu hình để hệ thống hỗ trợ song song TCP (cho Python) và WebSockets (cho Web). Kiểm tra kết nối bằng các công cụ test như MQTTX.

Cấu hình mosquitto broker hỗ trợ websockets 
Mặc định: mosquitto chỉ mở cổng 1883 chạy TCP chuẩn cho python 
Web: thì phải dùng websockets. Do đó, phải cấu hình để broker mở song song cả 2 cổng

Cổng 1883 cho Python Simulator (TCP thuần)
listener 1883
allow_anonymous true

Cổng 9001 cho React/Three.js Dashboard (WebSockets)
listener 9001
protocol websockets
allow_anonymous true

(file nano sudo nano /etc/mosquitto/mosquitto.conf)

3. **Python Publisher:** Viết script Python sinh ra một luồng dữ liệu góc quay cho đúng 1 khớp duy nhất (ví dụ: khớp_vai_trái). Đẩy liên tục dữ liệu này lên Broker.

Thiết lập kết nối MQTT cho Frontend và bơm dữ liệu từ python 

- Phía web (subcriber): cài thêm một thư viện MQTT client chạy trên trình duyệt để nó biết cách kết nối vào cổng 9001 (websockets) của mosquitto và ngồi "hóng" dữ liệu
- Phía python (publisher): kích hoạt lại venv của python để viết script ngắn bắn tạo độ thử nghiệm vào cổng 1883 

DONE 


4. **Hội tụ và Đồng bộ:** Cấu hình trang Web lắng nghe Topic của khớp_vai_trái. Khi nhận được con số radian từ Python, dùng mã JavaScript áp dụng phép xoay không gian 3D (Rotation/Quaternion) vào đúng bộ phận vai của mô hình.

Hướng 1: bóc tách joint hierachy

> Thay vì xoay cả cụm (toàn bộ quay quanh trục y). Bóc tách hệ xuong để tìm khớp. Khi đó script python sẽ không bắn dữ liệu chung chung mà sẽ phân nhánh cây topic

> + humanoid/hinematics/head -> điều khiển robot gật đầu 

> + humanoid/kinematics/left_arm -> điều khiển robot giơ tay vẫy chào 


5. update luồng dữ liệu thật từ camera (vẫn lỗi điều khiển tay trái, tay phải)

> +feat: integrate real-time upper body and dual hand tracking via MediaPipe Holistic

> +feat: connect python computer vision pipeline with mqtt publisher for humanoid teleoperation

> +fix: downgrade mediapipe to v0.10.14 to resolve solution attribute error
## TODO
Hướng 1: Kết nối với Bộ mô phỏng Vật lý (MuJoCo / PyBullet / Isaac Gym)
Thay vì dùng script Python sinh sóng sin giả lập, chúng ta sẽ viết một script Python khởi tạo một môi trường vật lý thực sự. Khi thuật toán điều khiển (hoặc mô hình Học tăng cường - Reinforcement Learning) tương tác và làm robot chuyển động trong MuJoCo, chúng ta sẽ trích xuất ma trận góc khớp thật đó để bắn qua MQTT, biến giao diện Web thành một Dashboard giám sát mô phỏng thời gian thực. (half done)

Hướng 2: Tối ưu hóa cấu trúc gói tin dữ liệu (JSON / MessagePack Serialization)
Hiện tại chúng ta đang bắn lẻ tẻ từng góc khớp trên các topic riêng biệt. Khi con robot phát triển lên đầy đủ các khớp ngón tay linh khéo (Dexterous Hands) và khớp chân, số lượng topic sẽ bùng nổ lên tới hàng chục. Chúng ta sẽ nâng cấp sang cấu trúc gói tin: Python đóng gói toàn bộ trạng thái góc của tất cả các khớp vào một cấu trúc JSON duy nhất rồi bắn qua một topic chung (ví dụ humanoid/state). Phía React sẽ nhận và phân rã gói tin để cập nhật toàn thân robot trong một khung hình duy nhất.


Tiếp: cho nhiều con pub hoạt động cùng nhau

_______________________
## DEPLOYMENT GUIDE 

**Bước 1: Khởi chạy MQTT Broker**

sudo systemctl restart mosquitto

> Kiểm tra xem 2 cổng 1883 và 9001 đã mở hay chưa

sudo ss -tulpn | grep mosquitto

**Bước 2: Khởi chạy Giao diện Web (Frontend)**

cd web_ui
npm run dev

**Bước 3: Kích hoạt luồng dữ liệu Động học (Backend Simulation)**

> Tại thư mục DigitalTwin

source ../.venv/bin/activate

python test_publisher.py


## FUTURE ROADMAP

1. **Vật lý hóa hệ thống:** Thay thế script sinh tọa độ toán học hình sin bằng việc nhúng trực tiếp bộ công cụ tính toán vật lý đa vật thể MuJoCo hoặc PyBullet ở tầng Backend.

2. **Tối ưu hóa băng thông (Serialization):** Nâng cấp phương thức truyền tin Plain Text hiện tại sang định dạng nén nhị phân MessagePack hoặc cấu trúc hóa chuỗi JSON để truyền tải toàn bộ trạng thái góc của 30+ khớp nối chỉ trong một gói tin duy nhất.





---
Tiếp:
1.Sử dụng brocker trên aws 
2.up web (vercel)
3.đóng gói python (dockerfile)
kiến trúc mt

___

timer counter ?? 2048 
lt ardunino 

wokwwi  (lib)

?? đất phải nối chung ??
hiệu điện thế ??
