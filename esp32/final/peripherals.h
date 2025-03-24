#ifndef SMARTHOME_PERIPHERALS_H
#define SMARTHOME_PERIPHERALS_H

#include "config.h"
#include "Led.h"

#include <Wire.h>
#include <string.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>



String readLCD();
String writeLCD(String message);
void clearLine(int line);
float getTemperature(bool celcius);
int getPotentiometer();
int getAll();
void setLedPins();
void setPotentiometer();
void createDefaultLeds();
void setLcd();
void setTemperature();
Led* getLed(int color);
int switchLed(int color, String state);
int getLedsSize();
int getLedStatus(int color);
int getLedIdByName(String color);

#endif