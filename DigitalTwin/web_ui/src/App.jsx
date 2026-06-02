import React, { Suspense, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage } from '@react-three/drei';
import mqtt from 'mqtt';

function HumanoidRobot({ robotRef }) {
  const { scene } = useGLTF('/models/humanoid.glb');

  // // Đoạn code kiểm tra hệ xương khớp của robot
  // React.useEffect(() => {
  //   console.log("====== DANH SÁCH TÊN CÁC KHỚP ROBOT ======");
  //   scene.traverse((child) => {
  //     // In ra tất cả các bộ phận có thể xoay được (Mesh, Bone, Group)
  //     if (child.name) {
  //       console.log(`Tên khớp: "${child.name}" | Loại: ${child.type}`);
  //     }
  //   });
  //   console.log("==========================================");
  // }, [scene]);

  return <primitive ref={robotRef} object={scene} scale={1.5} position={[0, 0, 0]} />;
}

export default function App() {
  const robotRef = useRef(null);

  useEffect(() => {
    const client = mqtt.connect('ws://localhost:9001');
    client.on('connect', () => {
      console.log('📡 Đã kết nối MQTT Broker!');
      // Đăng ký nghe topic tổng hợp phần thân trên
      client.subscribe('humanoid/kinematics/upper_body');
    });

    client.on('message', (topic, message) => {
      if (topic === 'humanoid/kinematics/upper_body' && robotRef.current) {
        try {
          const data = JSON.parse(message.toString());
          const jointAngles = data.joints;

          Object.keys(jointAngles).forEach((jointName) => {
            const joint = robotRef.current.getObjectByName(jointName);
            if (joint) {
              // Phân phối trục xoay tối ưu tùy thuộc vào loại khớp
              if (jointName.includes('Finger')) {
                // Ngón tay gập theo trục Z
                joint.rotation.z = jointAngles[jointName];
              } else if (jointName.includes('UpperArm')) {
                // Cánh tay trên vung lên xuống theo trục X hoặc Z tùy model, ta thử trục X
                joint.rotation.x = jointAngles[jointName];
              } else if (jointName.includes('Forearm')) {
                // Khủy tay gập duỗi ra trước
                joint.rotation.y = jointAngles[jointName];
              }
            }
          });
        } catch (error) {
          console.error("Lỗi parse JSON:", error);
        }
      }
    });

    return () => client.end();
  }, []);

  return (
    <div style={{ height: '100vh', width: '100vw', backgroundColor: '#111111' }}>
      <Canvas camera={{ position: [0, 2, 5], fov: 45 }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />
        <Suspense fallback={null}>
          <Stage intensity={0.5} environment="city" adjustCamera={false}>
            <HumanoidRobot robotRef={robotRef} />
          </Stage>
        </Suspense>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}