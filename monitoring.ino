#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);  // Ubah baud rate ke 9600
  lcd.init();
  lcd.backlight();
}

void loop() {
  if (Serial.available()) {
    String line1 = Serial.readStringUntil('\n');
    String line2 = Serial.readStringUntil('\n');
    
    Serial.print("Received Line 1: ");
    Serial.println(line1);
    Serial.print("Received Line 2: ");
    Serial.println(line2);

    lcd.clear();
    lcd.setCursor(0, 0);  // Baris 1
    lcd.print(line1);
    lcd.setCursor(0, 1);  // Baris 2
    lcd.print(line2);
  }
}
