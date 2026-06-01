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
    // Kết nối tới Broker qua cổng WebSockets
    const client = mqtt.connect('ws://localhost:9001');

    client.on('connect', () => {
      console.log('📡 Đã kết nối MQTT thành công!');
      // Đăng ký nhận TẤT CẢ dữ liệu động học bằng Wildcard '#'
      // Cấu trúc mong muốn: humanoid/kinematics/[Tên_Khớp]/[Trục_Xoay]
      client.subscribe('humanoid/kinematics/#');
    });

    client.on('message', (topic, message) => {
      // Phân tách chuỗi topic thành các mảng chữ
      // Ví dụ: "humanoid/kinematics/Head/y" -> ['humanoid', 'kinematics', 'Head', 'y']
      const parts = topic.split('/');
      
      if (parts[1] === 'kinematics' && robotRef.current) {
        const jointName = parts[2]; // Lấy ra tên khớp: VD "Head"
        const axis = parts[3] || 'y'; // Lấy ra trục xoay: x, y, hoặc z (mặc định là y)
        const angle = parseFloat(message.toString()); // Lấy góc xoay số thực

        if (!isNaN(angle)) {
          // DÙNG TOÁN HỌC THREE.JS: Tìm chính xác bộ phận có tên đó trong con robot
          const joint = robotRef.current.getObjectByName(jointName);
          
          if (joint) {
            // Ép khớp đó xoay quanh trục tương ứng theo thời gian thực!
            joint.rotation[axis] = angle;
          }
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