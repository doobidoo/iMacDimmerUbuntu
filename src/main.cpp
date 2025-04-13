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
  // digitalWrite(ledPin, HIGH); // Turn on LED
  
  // Configure PWM
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(pwmPin, pwmChannel);
  
  // Set initial brightness to 70%
  int initialBrightness = (70 * 255) / 100;
  ledcWrite(pwmChannel, initialBrightness);
}

String inputBuffer;

void loop() {
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 2000) {
    digitalWrite(ledPin, LOW);
    delay(50);
    digitalWrite(ledPin, HIGH);
    lastBlink = millis();
  }

  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      inputBuffer.trim();
      if (inputBuffer.length() > 0 && isDigit(inputBuffer.charAt(0))) {
        int percentBrightness = constrain(inputBuffer.toInt(), 0, 100);
        int pwmValue = map(percentBrightness, 0, 100, 0, 255);
        ledcWrite(pwmChannel, pwmValue);

        digitalWrite(ledPin, LOW);
        delay(100);
        digitalWrite(ledPin, HIGH);

        Serial.printf("Brightness set to: %d%%\n", percentBrightness);
      }
      inputBuffer = "";  // clear after processing
    } else {
      inputBuffer += c;
    }
  }
}
