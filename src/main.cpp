#include <Arduino.h>

// Define the PWM properties
const int pwmPin = 3;        // GPIO3 for PWM output
const int pwmFreq = 10000;   // 10kHz PWM frequency
const int pwmChannel = 0;    // PWM channel
const int pwmResolution = 8; // 8-bit resolution (0-255)
const int ledPin = 8;        // Built-in blue LED

void setup() {
  // Wait for USB to initialize
  delay(1000);
  
  // Configure Serial communication
  Serial.begin(115200);
  
  // Configure status LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); // Turn on LED
  
  // Configure PWM
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(pwmPin, pwmChannel);
  
  // Set initial brightness to 70%
  int initialBrightness = (70 * 255) / 100;
  ledcWrite(pwmChannel, initialBrightness);
}

void loop() {
  // Simple heartbeat
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 2000) {
    digitalWrite(ledPin, LOW);
    delay(50);
    digitalWrite(ledPin, HIGH);
    lastBlink = millis();
  }
  
  // Check for serial data with a simpler approach
  while (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove any whitespace
    
    // Process the input if it's a number
    if (input.length() > 0 && isDigit(input.charAt(0))) {
      int percentBrightness = input.toInt();
      percentBrightness = constrain(percentBrightness, 0, 100);
      
      // Convert to PWM value
      int pwmValue = map(percentBrightness, 0, 100, 0, 255);
      
      // Apply the brightness
      ledcWrite(pwmChannel, pwmValue);
      
      // Blink LED to confirm
      digitalWrite(ledPin, LOW);
      delay(100);
      digitalWrite(ledPin, HIGH);
      
      // Try to send confirmation (may not work)
      Serial.print("Brightness set to: ");
      Serial.print(percentBrightness);
      Serial.println("%");
    }
  }
}