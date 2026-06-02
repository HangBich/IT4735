import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import json
import math

# 1. Khởi tạo MQTT
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

# 2. Khởi tạo MediaPipe Holistic (Bản v0.10.14 hỗ trợ solutions)
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

def calculate_angle(p1, p2, p3):
    try:
        v1 = [p1.x - p2.x, p1.y - p2.y, p1.z - p2.z]
        v2 = [p3.x - p2.x, p3.y - p2.y, p3.z - p2.z]
        dot_prod = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        angle = math.acos(max(-1.0, min(1.0, dot_prod / (mag1 * mag2))))
        return max(0.0, math.pi - angle)
    except:
        return 0.0

cap = cv2.VideoCapture(0)
print("🚀 Đang chạy bộ lọc hai tay + cánh tay toàn diện...")

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue
        
        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(img_rgb)
        
        # Tạo sẵn cấu trúc JSON trống
        payload = {"joints": {}}
        
        # === XỬ LÝ PHẦN CÁNH TAY & KHỦY TAY (POSE) ===
        if results.pose_landmarks:
            plm = results.pose_landmarks.landmark
            # Vẽ khung xương thân người để test góc nhìn camera
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            
        # --- BÊN TRÁI (LEFT) ---
        # Góc khủy tay trái (Điểm 11: Vai, 13: Khủy tay, 15: Cổ tay)
        if results.left_hand_landmarks:
            print("👋 Đã nhận diện thấy TAY TRÁI trên Camera!")
            l_elbow_angle = calculate_angle(plm[11], plm[13], plm[15])
            # Góc vung cánh tay trên bên trái (Điểm 23: Hông, 11: Vai, 13: Khủy tay)
            l_shoulder_angle = calculate_angle(plm[23], plm[11], plm[13])
            
            payload["joints"]["ValveBipedBip01_L_Forearm_018"] = l_elbow_angle   # Khủy tay Trái
            payload["joints"]["ValveBipedBip01_L_UpperArm_017"] = l_shoulder_angle # Cánh tay Trái

            # --- BÊN PHẢI (RIGHT) ---
            # Góc khủy tay phải (Điểm 12: Vai, 14: Khủy tay, 16: Cổ tay)
            r_elbow_angle = calculate_angle(plm[12], plm[14], plm[16])
            # Góc vung cánh tay trên bên phải (Điểm 24: Hông, 12: Vai, 14: Khủy tay)
            r_shoulder_angle = calculate_angle(plm[24], plm[12], plm[14])
            
            # Lưu ý: Sửa lại chính xác mã khớp Tay Phải dựa vào console của bạn (thường đổi chữ _L_ thành _R_)
            payload["joints"]["ValveBipedBip01_R_Forearm_018"] = r_elbow_angle   
            payload["joints"]["ValveBipedBip01_R_UpperArm_017"] = r_shoulder_angle 

        # === XỬ LÝ CHI TIẾT NGÓN TAY TRÁI ===
        if results.left_hand_landmarks:
            mp_draw.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            l_lm = results.left_hand_landmarks.landmark
            payload["joints"]["ValveBipedBip01_L_Finger1_020"] = calculate_angle(l_lm[5], l_lm[6], l_lm[8])

        # === XỬ LÝ CHI TIẾT NGÓN TAY PHẢI ===
        if results.right_hand_landmarks:
            print("👋 Đã nhận diện thấy TAY PHẢI trên Camera!")
            mp_draw.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            r_lm = results.right_hand_landmarks.landmark
            # Áp góc gập ngón trỏ phải (thường khớp đối xứng sẽ đổi chữ _L_ thành _R_)
            payload["joints"]["ValveBipedBip01_R_Finger1_020"] = calculate_angle(r_lm[5], r_lm[6], r_lm[8])

        # Bắn toàn bộ vector trạng thái chi trên qua một topic duy nhất
        if payload["joints"]:
            client.publish("humanoid/kinematics/upper_body", json.dumps(payload))
            
        cv2.imshow("Holistic Real-time Teleop", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
            
except KeyboardInterrupt:
    print("\n🛑 Ngắt kết nối.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()