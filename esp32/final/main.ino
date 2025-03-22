#include "Led.h"
#include "peripherals.h"
#include "homewebserver.h"
#include "config.h"
#include <Wire.h>
#include <string.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <WebServer.h>


void setup() {
  Serial.begin(115200);
  setLedPins();
  setPotentiometer();
  createDefaultLeds();
  setLcd();
  writeLCD("Hi! DEMO");
  wifiSet();
  setEndpoints();
  Serial.println("HTTP server started");
  
}

void loop() {
  serverHandleClient();
  delay(2);

}