#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

// WiFi credentials
const char* ssid = "YOUR_SSID_HERE";
const char* password = "YOUR_PASSWORD_HERE";

// Web server
WebServer server(80);

// Firmware version
const char* FIRMWARE_VERSION = "1.6.0-dynamic-discovery";
const char* BUILD_DATE = __DATE__ " " __TIME__;

// Define the PWM properties
const int pwmPin = 3;        // GPIO3 for PWM output
const int pwmFreq = 10000;   // 10kHz PWM frequency
const int pwmChannel = 0;    // PWM channel
const int pwmResolution = 8; // 8-bit resolution (0-255)
const int ledPin = 8;        // Built-in blue LED

// Brightness level (0-255)
int brightness = 128;

// Function prototypes
void connectToWifi();
void setupWebServer();
String getWifiStatusJson();
String getHtmlPage();

void setup() {
  // Wait for USB to initialize
  delay(1000);
  
  // Configure Serial communication with explicit settings
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  delay(100);
  
  // Force serial output
  for (int i = 0; i < 5; i++) {
    Serial.println("=== ESP32-C3 SuperMini iMac Dimmer Starting ===");
    Serial.flush();
    delay(100);
  }
  
  Serial.print("Firmware Version: ");
  Serial.println(FIRMWARE_VERSION);
  Serial.print("Build Date: ");
  Serial.println(BUILD_DATE);
  Serial.println("Serial initialization complete!");
  Serial.flush();
  
  // Configure status LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  
  // Configure PWM
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(pwmPin, pwmChannel);
  
  // Set initial brightness to 70%
  int initialBrightness = (70 * 255) / 100;
  ledcWrite(pwmChannel, initialBrightness);
  brightness = initialBrightness;
  
  // Connect to WiFi and start web server
  connectToWifi();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected");
    
    // Start mDNS service
    if (MDNS.begin("imacdimmer")) {
      Serial.println("mDNS responder started");
      Serial.println("Hostname: imacdimmer.local");
      MDNS.addService("http", "tcp", 80);
      MDNS.addServiceTxt("http", "tcp", "device", "ESP32-C3");
      MDNS.addServiceTxt("http", "tcp", "function", "brightness_control");
    } else {
      Serial.println("Error starting mDNS");
    }
    
    setupWebServer();
    server.begin();
    Serial.println("Web server started");
    Serial.print("Access web interface at: http://");
    Serial.println(WiFi.localIP());
    Serial.println("Or via: http://imacdimmer.local");
  }
}

String inputBuffer;

void loop() {
  // Handle web server requests (non-blocking)
  server.handleClient();
  
  // Handle mDNS (ESP32 doesn't need explicit update)
  
  // Check WiFi connection (only occasionally)
  static unsigned long lastWiFiCheck = 0;
  if (millis() - lastWiFiCheck > 30000) { // Check every 30 seconds
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi connection lost. Reconnecting...");
      connectToWifi();
    }
    lastWiFiCheck = millis();
  }
  
  // Status LED blink every 2 seconds
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 2000) {
    digitalWrite(ledPin, LOW);
    delay(50);
    digitalWrite(ledPin, HIGH);
    lastBlink = millis();
    
    // Debug: Send periodic heartbeat to serial
    Serial.printf("Heartbeat: %lu, WiFi: %s, Brightness: %d\n", 
                  millis(), WiFi.status() == WL_CONNECTED ? "OK" : "NO", brightness);
    Serial.flush();
  }

  // Handle serial commands with timeout protection
  static unsigned long lastSerialActivity = millis();
  if (Serial.available() > 0) {
    lastSerialActivity = millis();
    char c = Serial.read();
    
    // Prevent buffer overflow
    if (inputBuffer.length() > 50) {
      inputBuffer = "";
    }
    
    if (c == '\n' || c == '\r') {
      inputBuffer.trim();
      if (inputBuffer.length() > 0) {
        Serial.printf("Received command: '%s'\n", inputBuffer.c_str());
        
        if (inputBuffer.equals("version")) {
          // Handle version command
          Serial.printf("Firmware: %s, Build: %s\n", FIRMWARE_VERSION, BUILD_DATE);
        } else if (inputBuffer.equals("ping")) {
          // Simple ping command
          Serial.println("pong");
        } else if (isDigit(inputBuffer.charAt(0))) {
          int percentBrightness = constrain(inputBuffer.toInt(), 0, 100);
          int pwmValue = map(percentBrightness, 0, 100, 0, 255);
          
          // Additional safety check
          if (percentBrightness < 5 && percentBrightness > 0) {
            Serial.println("Warning: minimum safe brightness is 5%");
          }
          
          // Apply brightness
          ledcWrite(pwmChannel, pwmValue);
          brightness = pwmValue;

          // Blink status LED to show command received
          digitalWrite(ledPin, LOW);
          delay(50);
          digitalWrite(ledPin, HIGH);

          Serial.printf("Brightness set to: %d%%\n", percentBrightness);
        } else {
          Serial.printf("Unknown command: '%s'\n", inputBuffer.c_str());
        }
        Serial.flush();
      }
      inputBuffer = "";  // clear after processing
    } else if (c >= 32 && c <= 126) { // Only accept printable characters
      inputBuffer += c;
    }
  }
  
  // Clear old input buffer if no activity for 5 seconds
  if (millis() - lastSerialActivity > 5000 && inputBuffer.length() > 0) {
    inputBuffer = "";
  }
  
  // Yield to other tasks
  yield();
}

void connectToWifi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int timeout = 20;
  while (WiFi.status() != WL_CONNECTED && timeout-- > 0) {
    digitalWrite(ledPin, !digitalRead(ledPin));
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(ledPin, HIGH);
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("\nWiFi connection failed. Continuing with serial-only mode.");
  }
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", getHtmlPage());
  });

  server.on("/wifistatus", HTTP_GET, []() {
    server.send(200, "application/json", getWifiStatusJson());
  });

  server.on("/version", HTTP_GET, []() {
    String json = "{";
    json += "\"firmware_version\": \"" + String(FIRMWARE_VERSION) + "\",";
    json += "\"build_date\": \"" + String(BUILD_DATE) + "\"";
    json += "}";
    server.send(200, "application/json", json);
  });

  server.on("/serial", HTTP_GET, []() {
    if (server.hasArg("cmd")) {
      String cmd = server.arg("cmd");
      String response = "";
      
      if (cmd == "version") {
        response = "Firmware: " + String(FIRMWARE_VERSION) + ", Build: " + String(BUILD_DATE);
      } else if (cmd == "ping") {
        response = "pong";
      } else if (cmd == "get") {
        int percent = map(brightness, 0, 255, 0, 100);
        response = "Current brightness: " + String(percent) + "%";
      } else if (cmd.toInt() > 0 && cmd.toInt() <= 100) {
        int percentBrightness = constrain(cmd.toInt(), 0, 100);
        int pwmValue = map(percentBrightness, 0, 100, 0, 255);
        ledcWrite(pwmChannel, pwmValue);
        brightness = pwmValue;
        
        // Blink LED to show command received
        digitalWrite(ledPin, LOW);
        delay(50);
        digitalWrite(ledPin, HIGH);
        
        response = "Brightness set to: " + String(percentBrightness) + "%";
      } else {
        response = "Unknown command: " + cmd;
      }
      
      server.send(200, "text/plain", response);
    } else {
      server.send(400, "text/plain", "Missing 'cmd' parameter");
    }
  });

  server.on("/led", HTTP_GET, []() {
    String ledPin = server.arg("pin");
    String ledState = server.arg("state");

    int pin = ledPin.toInt();
    int state = ledState.toInt();

    if (pin == 8) {
      digitalWrite(pin, state ? LOW : HIGH);
      server.send(200, "text/plain", "LED on pin " + ledPin + " set to " + ledState);
    } else {
      server.send(400, "text/plain", "Invalid LED pin");
    }
  });

  server.on("/brightness", HTTP_GET, []() {
    if (server.hasArg("level")) {
      int newBrightness = constrain(server.arg("level").toInt(), 0, 255);
      ledcWrite(pwmChannel, newBrightness);
      brightness = newBrightness;
      int percentBrightness = map(newBrightness, 0, 255, 0, 100);
      Serial.printf("Web: Brightness set to: %d%% (%d/255)\n", percentBrightness, newBrightness);
      server.send(200, "text/plain", "Brightness set to " + String(newBrightness));
    } else {
      server.send(400, "text/plain", "Missing 'level' parameter");
    }
  });

  server.onNotFound([]() {
    server.send(404, "text/plain", "Not found");
  });
}

String getWifiStatusJson() {
  String json = "{";
  json += "\"connected\": " + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
  json += "\"ssid\": \"" + String(ssid) + "\",";
  json += "\"rssi\": " + String(WiFi.RSSI()) + ",";
  json += "\"ip\": \"" + WiFi.localIP().toString() + "\",";
  json += "\"brightness\": " + String(brightness) + ",";
  json += "\"firmware_version\": \"" + String(FIRMWARE_VERSION) + "\",";
  json += "\"build_date\": \"" + String(BUILD_DATE) + "\"";
  json += "}";
  return json;
}

String getHtmlPage() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>iMac Display Brightness Control</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4; color: #333; }
    h1 { color: #2c3e50; }
    .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .btn { background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 5px; margin-right: 10px; cursor: pointer; }
    .btn.off { background: #e74c3c; }
    .slider { width: 100%; }
    .brightness-display { font-size: 24px; font-weight: bold; color: #2c3e50; }
  </style>
</head>
<body>
  <h1>iMac Display Brightness Control</h1>

  <div class="card">
    <h2>WiFi Status</h2>
    <div id="wifi-status">Loading...</div>
  </div>

  <div class="card">
    <h2>Status LED Control</h2>
    <button class="btn" onclick="toggleLed(8, 1)">LED ON</button>
    <button class="btn off" onclick="toggleLed(8, 0)">LED OFF</button>
  </div>

  <div class="card">
    <h2>Display Brightness</h2>
    <input type="range" min="0" max="255" value="128" class="slider" id="brightnessSlider" onchange="setBrightness(this.value)">
    <p class="brightness-display">Current: <span id="brightnessValue">128</span>/255 (<span id="brightnessPercent">50</span>%)</p>
    <div style="margin-top: 10px;">
      <button class="btn" onclick="setPresetBrightness(13)">5%</button>
      <button class="btn" onclick="setPresetBrightness(51)">20%</button>
      <button class="btn" onclick="setPresetBrightness(128)">50%</button>
      <button class="btn" onclick="setPresetBrightness(179)">70%</button>
      <button class="btn" onclick="setPresetBrightness(255)">100%</button>
    </div>
  </div>

  <div class="card">
    <h2>System Info</h2>
    <p><strong>Device:</strong> ESP32-C3 SuperMini</p>
    <p><strong>Purpose:</strong> iMac Display Brightness Control</p>
    <p><strong>CPU Frequency:</strong> )rawliteral" + String(ESP.getCpuFreqMHz()) + R"rawliteral( MHz</p>
    <p><strong>Flash Size:</strong> )rawliteral" + String(ESP.getFlashChipSize() / 1024 / 1024) + R"rawliteral( MB</p>
    <p><strong>Free Heap:</strong> )rawliteral" + String(ESP.getFreeHeap() / 1024) + R"rawliteral( KB</p>
  </div>

  <script>
    function updateWiFiStatus() {
      fetch('/wifistatus')
        .then(response => response.json())
        .then(data => {
          document.getElementById('wifi-status').innerHTML = `
            <p><strong>Connected:</strong> ${data.connected ? 'Yes' : 'No'}</p>
            <p><strong>SSID:</strong> ${data.ssid}</p>
            <p><strong>Signal Strength:</strong> ${data.rssi} dBm</p>
            <p><strong>IP Address:</strong> ${data.ip}</p>
            <p><strong>Current Brightness:</strong> ${data.brightness}/255</p>
            <p><strong>Firmware:</strong> ${data.firmware_version}</p>
            <p><strong>Build Date:</strong> ${data.build_date}</p>`;
          
          // Update slider if brightness changed via serial
          if (data.brightness !== undefined) {
            document.getElementById('brightnessSlider').value = data.brightness;
            document.getElementById('brightnessValue').innerText = data.brightness;
            document.getElementById('brightnessPercent').innerText = Math.round((data.brightness / 255) * 100);
          }
        })
        .catch(error => {
          document.getElementById('wifi-status').innerHTML = '<p style="color: red;">Error loading WiFi status</p>';
        });
    }

    function toggleLed(pin, state) {
      fetch(`/led?pin=${pin}&state=${state}`)
        .then(response => response.text())
        .then(console.log)
        .catch(error => console.error('LED control error:', error));
    }

    function setBrightness(level) {
      fetch(`/brightness?level=${level}`)
        .then(response => response.text())
        .then(console.log)
        .catch(error => console.error('Brightness control error:', error));
      
      document.getElementById("brightnessValue").innerText = level;
      document.getElementById("brightnessPercent").innerText = Math.round((level / 255) * 100);
    }

    function setPresetBrightness(level) {
      document.getElementById('brightnessSlider').value = level;
      setBrightness(level);
    }

    // Initialize
    updateWiFiStatus();
    setInterval(updateWiFiStatus, 5000);
  </script>
</body>
</html>
)rawliteral";
  return html;
}