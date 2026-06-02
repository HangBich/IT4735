import mujoco
import mujoco.viewer
import paho.mqtt.client as mqtt
import json
import time

# 1. Khởi tạo MQTT kết nối sang Web Dashboard
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

# 2. Nạp file cấu hình vật lý robot vào MuJoCo
model = mujoco.MjModel.from_xml_path('humanoid.xml')
data = mujoco.MjData(model)

print("🚀 Bộ mô phỏng vật lý MuJoCo đang khởi chạy...")
print("Dữ liệu góc khớp thực tế sẽ được đồng bộ sang Web UI thời gian thực.")

# 3. Mở cửa sổ tương tác mô phỏng của MuJoCo
with mujoco.viewer.launch_passive(model, data) as viewer:
    
    # Đặt mục tiêu điều khiển lực ban đầu cho các khớp
    # Trong RL, mảng ctrl này chính là "Action" do mô hình AI quyết định
    data.ctrl[0] = 0.0  # Lực điều khiển khớp đầu
    data.ctrl[1] = 0.0  # Lực điều khiển cánh tay trái

    sim_time = 0.0
    
    while viewer.is_running():
        step_start = time.time()

        # Giả lập một thuật toán điều khiển: Bơm lực hình sin vào cánh tay vật lý
        # Robot trong MuJoCo sẽ chịu tác động của trọng lực và lực cản vật lý thực tế
        data.ctrl[1] = 5.0 * json.loads(str(time.time() % 1)) # Ví dụ lực thay đổi tuần hoàn
        
        # Tiến một bước mô phỏng vật lý (Tính toán vận tốc, gia tốc, va chạm)
        mujoco.mj_step(model, data)
        
        # 4. Trích xuất GÓC KHỚP VẬT LÝ THỰC TẾ (qpos)
        # MuJoCo trả về mảng tọa độ qpos, ta đọc theo tên khớp bằng hàm mj_name2id
        head_joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "ValveBipedBip01_Head1_014")
        arm_joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "ValveBipedBip01_L_UpperArm_017")
        
        real_head_angle = data.qpos[head_joint_id]
        real_arm_angle = data.qpos[arm_joint_id]

        # 5. Đóng gói JSON truyền sang Digital Twin trên Web
        payload = {
            "joints": {
                "ValveBipedBip01_Head1_014": real_head_angle,
                "ValveBipedBip01_L_UpperArm_017": real_arm_angle
            }
        }
        client.publish("humanoid/kinematics/upper_body", json.dumps(payload))
        
        # Cập nhật hiển thị lên app xem của MuJoCo
        viewer.sync()

        # Đồng bộ thời gian thực mô phỏng (0.01 giây mỗi step)
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)

client.disconnect()