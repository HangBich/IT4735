import requests
import json
import time

API_KEY = "T7H40F0X82VGW7L5"
FIELD1_VAL = 20
FIELD2_VAL = 33

def send_data_way_1():
    """
    Cách 1: Gửi dữ liệu qua phương thức GET.
    Các trường field1, field2 được đóng gói trực tiếp trong URL (urlencoded).
    """
    print("--- Đang thực hiện Cách 1: Gửi qua GET (urlencoded) ---")
    url = "https://api.thingspeak.com/update"
    
    params = {
        "api_key": API_KEY,
        "field1": FIELD1_VAL,
        "field2": FIELD2_VAL
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print(f"URL thực tế đã gọi: {response.url}")
            print(f"Phản hồi từ ThingSpeak (ID của entry mới): {response.text}")
        else:
            print(f"Lỗi hệ thống! Mã trạng thái: {response.status_code}")
            
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kết nối: {e}")


def send_data_way_2():
    """
    Cách 2: Gửi dữ liệu qua phương thức POST.
    Các trường field1, field2 được đóng gói trong body request bằng JSON.
    """
    print("\n--- Đang thực hiện Cách 2: Gửi qua POST (JSON Body) ---")
    
    url = f"https://api.thingspeak.com/update?api_key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    body_payload = {
        "field1": FIELD1_VAL,
        "field2": FIELD2_VAL
    }
    
    try:
        response = requests.post(url, json=body_payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Body gửi đi: {json.dumps(body_payload, indent=4)}")
            print(f"Phản hồi từ ThingSpeak (ID của entry mới): {response.text}")
        else:
            print(f"Lỗi hệ thống! Mã trạng thái: {response.status_code}")
            
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kết nối: {e}")

def get_and_parse_thingspeak_data():
    url = "https://api.thingspeak.com/channels/1529099/feeds.json?results=2"
    
    print(f"--- Đang gửi GET request đến: {url} ---")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            feeds = data.get("feeds", [])
            
            print(f"\nTìm thấy {len(feeds)} bản ghi gần nhất:\n")
            
            for index, feed in enumerate(feeds, start=1):
                temperature = feed.get("field1")
                humidity = feed.get("field2")
                created_at = feed.get("created_at")
                
                print(f"--- Bản ghi thứ {index} ({created_at}) ---")
                print(f" * Temperature (field1): {temperature}")
                print(f" * Humidity (field2)   : {humidity}")
                print("-" * 40)
                
        else:
            print(f"Lấy dữ liệu thất bại. Mã lỗi HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kết nối mạng: {e}")

if __name__ == "__main__":
    # Chạy Cách 1
    send_data_way_1()
    
    # Timegap tối thiểu 15s 
    print("\nĐang đợi 15 giây để tránh giới hạn Rate Limit của ThingSpeak...")
    time.sleep(15)
    
    # Chạy Cách 2
    send_data_way_2()

    # b) lấy dữ liệu về từ Thingpeak API
    get_and_parse_thingspeak_data()
