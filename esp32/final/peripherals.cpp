#include "peripherals.h"

/*
==============================================
                  GLOBALS
==============================================
*/

OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature sensors(&oneWire);
float temperatureC;
float temepratureF;

LedArray leds;

int potentiometer;

LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);

String currentMessage;

/*
==============================================
                      LEDS
==============================================
*/

void setLedPins() {
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);
}

void createDefaultLeds(){
  leds.leds[RED] = new Led("RED", RED, LED_RED_PIN);
  leds.leds[GREEN] = new Led("GREEN", GREEN, LED_GREEN_PIN);
  leds.leds[BLUE] = new Led("BLUE", BLUE, LED_BLUE_PIN);
}

Led* getLed(int color) {
  if (color >= 0 && color < NUM_OF_LEDS) {
      return leds.leds[color];
    }
    return nullptr;
}

int getLedStatus(int color) {
  if (color >= 0 && color < NUM_OF_LEDS) {
    return leds.leds[color]->getStatus();
  }
  else {
    return -1;
  }
}

int getLedsSize() {
  return leds.size;
}

int switchLed(int color, String state) {
  if (color < leds.size) {
    Led* currentLed = getLed(color);
    currentLed->changeLedState(state);
    return (int)currentLed->getStatus();
  }
  else {
    return -1;
  }
}

int getLedIdByName(String name) {
  for (int i=0; i<leds.size; i++)
  {
    if (name.equalsIgnoreCase(getLed(i)->getName())){
      return getLed(i)->getColor();
    }
  }
  return -1;
}

/*
==============================================
                    LCD
==============================================
*/

void setLcd() {
  lcd.init();
  lcd.begin(16, 2);
  lcd.backlight();
}

String readLCD() {
  return currentMessage;
}

void clearLine(int line){
  lcd.setCursor(0,line);
  lcd.print("                ");
  lcd.setCursor(0,line);
}

String writeLCD(String message) {
  lcd.clear();
  currentMessage = message;
  int slice = 0;
  int n = message.length();
  if (n <= 16) {
    lcd.setCursor(0,0);
    lcd.print(message);
    return message;
  }
  while (n > 16) {
    clearLine(0);
    lcd.print(message.substring(slice, slice+16));
    slice+=16;
    delay(SCROLL_DELAY);
    clearLine(1);
    lcd.print(message.substring(slice, slice+16));
    slice+=16;
    n -=32;
    delay(SCROLL_DELAY << 1);
  }
  if (n<=0)
    return message;
  clearLine(0);
  lcd.print(message.substring(slice, slice + n));
  return message;
}

/*
==============================================
                Potentiometer
==============================================
*/

void setPotentiometer(){
  pinMode(POTENTIOMETER_PIN, INPUT);
}

int getPotentiometer() {
  int adc_val = analogRead(POTENTIOMETER_PIN);
  float tempVal = (float)adc_val / 4095.00; 
  return (int)(MAX_RESISTANCE * tempVal);

  // need to add the calculation of voltage divider
}

/*
==============================================
                Temperature
==============================================
*/

void setTemperature(){
  sensors.begin();
}

float getTemperature(bool celcius) {
  sensors.requestTemperatures();
  if (celcius) {
    temperatureC = sensors.getTempCByIndex(0);
    return temperatureC;
  }
  else {
    temepratureF = sensors.getTempFByIndex(0);
    return temepratureF;
  }
}
