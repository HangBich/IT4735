import paho.mqtt.client as mqtt
import time
import math

# Khởi tạo client kết nối (Tương thích với paho-mqtt v2.x)
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

print("🚀 Đang bơm dữ liệu điều khiển khớp thời gian thực vào Digital Twin...")
print("Nhấn Ctrl + C để dừng.")

time_step = 0.0

try:
    while True:
        # 1. Điều khiển cái Đầu (Lắc đầu qua lại)
        # Biên độ nhỏ 0.4 radian để chuyển động tự nhiên
        head_angle = math.sin(time_step) * 0.4
        client.publish("humanoid/kinematics/ValveBipedBip01_Head1_014/y", str(head_angle))
        
        # 2. Điều khiển Cánh tay trái (Vung tay lên xuống)
        # Sử dụng cos và đổi trục (ví dụ trục z hoặc x tùy hướng đặt xương, ta thử trục x trước)
        arm_angle = math.cos(time_step * 1.2) * 0.6
        client.publish("humanoid/kinematics/ValveBipedBip01_L_UpperArm_017/y", str(arm_angle))
        
        # Tăng tiến trình thời gian
        time_step += 0.05
        
        # Gửi dữ liệu ở tần số ~33Hz (30ms một lần) cho mượt mà
        time.sleep(0.03)

except KeyboardInterrupt:
    print("\n🛑 Đã ngắt luồng phát tín hiệu.")
    client.disconnect()