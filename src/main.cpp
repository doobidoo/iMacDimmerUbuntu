#include <Arduino.h>

// Define the PWM properties
const int pwmPin = 23;        // GPIO23/D23 for PWM output
const int pwmFreq = 10000;    // 10kHz PWM frequency
const int pwmChannel = 0;     // PWM channel (0-15)
const int pwmResolution = 8;  // 8-bit resolution (0-255)
const int ledPin = 2;         // Built-in LED for status

void setup() {
  // Configure Serial communication
  Serial.begin(115200);
  
  // Configure status LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);  // Turn on LED to show we're running
  
  // Configure PWM
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(pwmPin, pwmChannel);
  
  // Set initial brightness to 70%
  int initialBrightness = (70 * 255) / 100;
  ledcWrite(pwmChannel, initialBrightness);
  
  Serial.println("ESP32 LCD Brightness Control Ready");
  Serial.println("Send values 0-100 for brightness percentage");
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming brightness value
    String input = Serial.readStringUntil('\n');
    int percentBrightness = input.toInt();
    
    // Convert percentage (0-100) to PWM value (0-255)
    // Enforce minimum brightness of 0%
    percentBrightness = constrain(percentBrightness, 0, 100);
    int pwmValue = map(percentBrightness, 0, 100, 0, 255);
    
    // Additional safety check
    if (pwmValue < 13) {
        //pwmValue = 13;  // Minimum safe brightness
        Serial.println("Warning: a minimum safe brightness is 5%");
    }
    
    // Apply the brightness
    ledcWrite(pwmChannel, pwmValue);
    
    // Blink status LED to show we received command
    digitalWrite(ledPin, LOW);
    delay(50);
    digitalWrite(ledPin, HIGH);
    
    // Send confirmation
    Serial.print("Brightness set to: ");
    Serial.print(percentBrightness);
    Serial.println("%");
  }
}