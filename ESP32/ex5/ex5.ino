#include <WiFi.h>              // [cite: 24]
#include <HTTPClient.h>        // [cite: 25]
#include <ArduinoJson.h>       // [cite: 26, 66]

// Cấu hình WiFi cho Wokwi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Cấu hình Server
String serverNameGet = "https://postman-echo.com/get";
String serverNamePost = "https://postman-echo.com/post"; // [cite: 27]

void setup() {
  Serial.begin(9600);          // [cite: 30]
  Serial.print("Connecting to WiFi"); // [cite: 31]
  
  WiFi.begin(ssid, password, 6); // [cite: 33]
  
  while (WiFi.status() != WL_CONNECTED) { // [cite: 34]
    delay(100);                // [cite: 35]
    Serial.print(".");         // [cite: 36]
  }
  Serial.println("\nWiFi Connected!"); // [cite: 38]
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) { // [cite: 41]
    // Dữ liệu mô phỏng (trong thực tế sẽ đọc từ cảm biến DHT22 và PIR)
    float x = 30.5; // Giá trị nhiệt độ [cite: 43, 67]
    float y = 78.0; // Giá trị độ ẩm [cite: 44, 68]
    int motion = 1; // Giá trị cảm biến chuyển động

    Serial.println("\n--- a) Gửi HTTP GET (url-encoded) ---");
    sendHTTPGet(x, y, motion);

    Serial.println("\n--- b) Gửi HTTP POST (url-encoded) ---");
    sendHTTPPostUrlEncoded(x, y, motion);

    Serial.println("\n--- c) Gửi HTTP POST (JSON) ---");
    sendHTTPPostJson(x, y, motion);

  } else {
    Serial.println("WiFi Disconnected"); // [cite: 62]
  }
  
  delay(10000); // Chờ 10 giây trước khi gửi lại
}

// a) Hàm gửi HTTP GET request, dữ liệu url-encoded
void sendHTTPGet(float temp, float humid, int motion) {
  HTTPClient http;
  String url = serverNameGet + "?temp=" + String(temp) + "&humid=" + String(humid) + "&motion=" + String(motion);
  
  http.begin(url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: "); Serial.println(httpResponseCode);
    String payload = http.getString();
    Serial.println(payload);
  } else {
    Serial.print("Error code: "); Serial.println(httpResponseCode);
  }
  http.end();
}

// b) Hàm gửi HTTP POST request, dữ liệu url-encoded
void sendHTTPPostUrlEncoded(float temp, float humid, int motion) {
  HTTPClient http;
  http.begin(serverNamePost);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  
  String httpRequestData = "temp=" + String(temp) + "&humid=" + String(humid) + "&motion=" + String(motion);
  Serial.println(httpRequestData);
  
  int httpResponseCode = http.POST(httpRequestData);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: "); Serial.println(httpResponseCode);
    String payload = http.getString();
    Serial.println(payload);
  } else {
    Serial.print("Error code: "); Serial.println(httpResponseCode);
  }
  http.end();
}

// c) Hàm gửi HTTP POST request, dữ liệu đóng gói JSON trong body
void sendHTTPPostJson(float temp, float humid, int motion) {
  HTTPClient http; // [cite: 42]
  http.begin(serverNamePost); // [cite: 45]
  http.addHeader("Content-Type", "application/json"); // [cite: 46]
  
  // Sử dụng thư viện ArduinoJson để đóng gói dữ liệu
  DynamicJsonDocument doc(1024); // [cite: 69]
  JsonObject root = doc.to<JsonObject>(); // [cite: 71]
  root["temperature"] = temp; // [cite: 72]
  root["humidity"] = humid;   // [cite: 73]
  root["motion"] = motion;
  
  String jsonstr; // [cite: 70]
  serializeJson(doc, jsonstr); // [cite: 74]
  
  Serial.println(jsonstr); // [cite: 49]
  
  int httpResponseCode = http.POST(jsonstr); // [cite: 50]
  
  if (httpResponseCode > 0) { // [cite: 51]
    Serial.print("HTTP Response code: "); Serial.println(httpResponseCode); // [cite: 52]
    String payload = http.getString(); // [cite: 53]
    Serial.println(payload); // [cite: 54]
  } else { // [cite: 56]
    Serial.print("Error code: "); Serial.println(httpResponseCode); // [cite: 57]
  }
  http.end(); // [cite: 59]
}