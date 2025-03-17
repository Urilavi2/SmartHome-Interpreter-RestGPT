#ifndef SMARTHOME_LED_H
#define SMARTHOME_LED_H
#include <Wire.h>

#include "config.h"

class Led{
  private:
      char* name;
      int color;
      bool status;
      int pin;
  public:
  Led(char* selfName, int selfColor, const int pinout);
  Led();
  ~Led();
  int getStatus();
  char* getName();
  void changeLedState(); 
  int getColor();
  
};

struct LedArray {
  Led* leds[NUM_OF_LEDS];
  int size=NUM_OF_LEDS;
};
#endif