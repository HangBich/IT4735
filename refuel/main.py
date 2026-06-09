import flet as ft
import paho.mqtt.client as mqtt

# --- CẤU HÌNH HIVEMQ CLOUD ---
BROKER = "71bbb0c00fe040c78a223714c93ff1ee.s1.eu.hivemq.cloud" 
PORT = 8883                                                    
MQTT_USER = "user_cayxang"               
MQTT_PASS = "Pass_cayxang123"

# --- ĐỊNH NGHĨA TOPIC ---
TOPIC_LENH = "cayxang/lenh"
TOPIC_TRANGTHAI = "cayxang/trangthai"
TOPIC_LUONGXANG = "cayxang/luongxang"
TOPIC_KETQUA = "cayxang/ketqua"
TOPIC_GIA = "cayxang/gia"         # Topic mới để cập nhật giá xăng

# Biến toàn cục lưu trữ giá xăng (mặc định ban đầu là 25000)
PRICE_PER_LITER = 25000  

def main(page: ft.Page):
    global PRICE_PER_LITER
    page.title = "Trạm Bơm Thông Minh"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO 

    target_liters = 1.0 
    is_my_order = False

    # --- KHỞI TẠO CÁC BIẾN GIAO DIỆN ---
    txt_status = ft.Text("Trạng thái: Đang kết nối...", size=20, color="orange")
    
    # Dòng hiển thị bảng giá xăng hiện tại của trạm
    txt_price_display = ft.Text(f"Đơn giá: {PRICE_PER_LITER:,} VNĐ/Lít", size=18, weight=ft.FontWeight.W_500, color="bluegrey")
    
    input_liters = ft.TextField(label="Nhập số lít cần bơm", width=300, keyboard_type=ft.KeyboardType.NUMBER)
    txt_display = ft.Text("0.0 L", size=40, weight=ft.FontWeight.BOLD, color="blue")
    
    txt_receipt = ft.Text("", size=22, weight=ft.FontWeight.W_600, color="green", visible=False)
    img_qr = ft.Image(src="", width=250, height=250, visible=False)
    
    # Nút bấm thế hệ mới (FilledButton) tự động đổi màu theo trạng thái disabled
    btn_start = ft.FilledButton(
        "BẮT ĐẦU BƠM", 
        width=300, 
        height=50, 
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DISABLED: "grey300", ft.ControlState.DEFAULT: "green"},
            color={ft.ControlState.DISABLED: "grey600", ft.ControlState.DEFAULT: "white"}
        )
    )

    # Nút bấm giả lập hệ thống ngân hàng xác nhận đã nhận tiền (Mặc định ẩn)
    btn_mock_payment = ft.FilledButton(
        "ĐÃ THANH TOÁN THÀNH CÔNG (MOCK BANK)",
        width=300,
        height=50,
        color="white",
        bgcolor="bluegrey700",
        visible=False
    )

    # --- THIẾT KẾ BÌNH XĂNG TRỰC QUAN ---
    fuel_liquid = ft.Container(
        bgcolor="amber",
        width=140,
        height=0,  
        border_radius=ft.BorderRadius(top_left=0, top_right=0, bottom_left=7, bottom_right=7),
        animate_size=ft.Animation(400, "easeOut")
    )

    tank_visual = ft.Container(
        content=fuel_liquid,
        width=150,
        height=250, 
        border=ft.Border.all(4, "bluegrey700"), 
        border_radius=12,
        bgcolor="grey100",  
        alignment=ft.Alignment(0, 1), 
        padding=1
    )

    # --- HÀM XỬ LÝ SỰ KIỆN MQTT ---
    def on_connect(client, userdata, flags, rc, *extra_params):
        print("Đã kết nối HiveMQ Cloud!")
        client.subscribe(TOPIC_TRANGTHAI)
        client.subscribe(TOPIC_LUONGXANG)
        client.subscribe(TOPIC_KETQUA)
        client.subscribe(TOPIC_GIA) # Đăng ký lắng nghe thêm topic giá
        txt_status.value = "Trạng thái: Đã kết nối mạng"
        page.update()

    def on_message(client, userdata, msg):
        global PRICE_PER_LITER
        nonlocal target_liters, is_my_order 
        
        topic = msg.topic
        payload = msg.payload.decode()

        # 1. Cập nhật giá xăng thực tế khi nhận được tin nhắn mới
        if topic == TOPIC_GIA:
            try:
                PRICE_PER_LITER = int(payload)
                txt_price_display.value = f"Đơn giá: {PRICE_PER_LITER:,} VNĐ/Lít"
            except Exception as e:
                print(f"Lỗi định dạng giá xăng: {e}")

        # 2. Khóa/Mở nút bấm và phân chia trạng thái hiển thị
        elif topic == TOPIC_TRANGTHAI:
            if payload == "READY":
                txt_status.value = "Trạng thái: SẴN SÀNG"
                txt_status.color = "green"
                btn_start.disabled = False
            elif payload == "BUSY":
                if is_my_order:
                    txt_status.value = "Trạng thái: ĐANG BƠM XĂNG..."
                    txt_status.color = "blue"
                else:
                    txt_status.value = "Trạng thái: HỆ THỐNG ĐANG BẬN (MÁY KHÁC ĐANG SỬ DỤNG)"
                    txt_status.color = "red"
                btn_start.disabled = True
        
        # 3. Xử lý số lít nhảy realtime (ĐÃ THÊM KHÓA BẢO VỆ)
        elif topic == TOPIC_LUONGXANG:
            # CHỈ máy nào phát lệnh bơm thì bình xăng mới đầy dần lên
            if is_my_order: 
                try:
                    current_liters = float(payload)
                    txt_display.value = f"{current_liters} L"
                    percentage = min(current_liters / target_liters, 1.0)
                    fuel_liquid.height = percentage * 240
                    
                    if percentage > 0.95:
                        fuel_liquid.border_radius = ft.BorderRadius(top_left=7, top_right=7, bottom_left=7, bottom_right=7)
                    else:
                        fuel_liquid.border_radius = ft.BorderRadius(top_left=0, top_right=0, bottom_left=7, bottom_right=7)
                except Exception as e:
                    print(f"Lỗi tính toán mực xăng: {e}")
            else:
                # Máy của người khác thì giữ nguyên bình rỗng, không cho nhảy số lung tung
                txt_display.value = "0.0 L"
                fuel_liquid.height = 0

        # 4. Kết thúc và Tính tiền (ĐA THÊM KHÓA BẢO VỆ)
        elif topic == TOPIC_KETQUA:
            if payload == "DONE":
                if is_my_order:
                    try:
                        final_liters = float(txt_display.value.replace(" L", ""))
                        total_money = int(final_liters * PRICE_PER_LITER)
                        
                        qr_url = f"https://img.vietqr.io/image/MB-0987654321-compact2.jpg?amount={total_money}&addInfo=TramXang_ThanhToan_{final_liters}L"
                        
                        txt_receipt.value = f"Tổng tiền cần trả: {total_money:,} VNĐ"
                        txt_receipt.visible = True
                        img_qr.src = qr_url
                        img_qr.visible = True
                        
                        # THÊM DÒNG NÀY: Hiện nút giả lập thanh toán lên cho bạn bấm test
                        btn_mock_payment.visible = True
                        
                        txt_status.value = "Trạng thái: HOÀN THÀNH - VUI LÒNG THANH TOÁN"
                        txt_status.color = "blue"
                    except Exception as ex:
                        print(f"Lỗi xử lý hóa đơn: {ex}")
                    
                    is_my_order = False
                else:
                    # Các máy phụ khác chỉ hiện thông báo đơn hàng của người kia đã xong, không hiện QR
                    txt_status.value = "Trạng thái: Trạm vừa bơm xong - Chờ khách thanh toán..."
                    txt_status.color = "orange"
                    txt_display.value = "0.0 L"
                    fuel_liquid.height = 0

        page.update()

    def mock_payment_success(e):
        # Tự đóng vai ngân hàng bắn READY lên để đưa trạm bơm về trạng thái SẴN SÀNG
        mqtt_client.publish(TOPIC_TRANGTHAI, "READY", retain=True)
        # Ẩn chính nó và ẩn QR đi để reset giao diện
        btn_mock_payment.visible = False
        img_qr.visible = False
        txt_receipt.visible = False
        page.update()

    btn_mock_payment.on_click = mock_payment_success

    # --- KHỞI TẠO MQTT CLIENT ---
    try:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        mqtt_client = mqtt.Client()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.tls_set() 

    mqtt_client.connect(BROKER, PORT)
    mqtt_client.loop_start()

    # --- HÀM XỬ LÝ SỰ KIỆN BẤM NÚT ---
    def start_pumping(e):
        nonlocal target_liters, is_my_order
        target = input_liters.value
        if target.replace('.', '', 1).isdigit(): 
            target_liters = float(target) if float(target) > 0 else 1.0
            is_my_order = True
            
            img_qr.visible = False
            txt_receipt.visible = False
            txt_display.value = "0.0 L"
            fuel_liquid.height = 0  
            
            # 1. Gửi lệnh bơm đi cho ESP32 nghe
            mqtt_client.publish(TOPIC_LENH, f"START:{target}")
            
            # 2. THÊM DÒNG NÀY: Tự động báo BUSY lên Cloud để KHÓA toàn bộ các máy khác ngay lập tức!
            mqtt_client.publish(TOPIC_TRANGTHAI, "BUSY", retain=True)
            
            btn_start.disabled = True 
            txt_status.value = "Đang gửi lệnh đến trạm bơm..."
            input_liters.value = ""
            page.update()

    btn_start.on_click = start_pumping

    # --- BỐ TRÍ GIAO DIỆN WEB ---
    page.add(
        ft.Container(height=20), 
        ft.Text("⛽ TRẠM XĂNG TỰ ĐỘNG SMART-IOT", size=26, weight=ft.FontWeight.BOLD),
        txt_status,
        txt_price_display,
        ft.Divider(height=20),
        input_liters,
        btn_start,
        ft.Container(height=15),
        tank_visual, 
        txt_display,
        ft.Divider(height=20),
        txt_receipt,
        ft.Container(height=10),
        img_qr,
        btn_mock_payment, # THẢ NÚT VÀO ĐÂY
        ft.Container(height=50)
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
