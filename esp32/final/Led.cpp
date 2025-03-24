#include "Led.h"

Led::Led(String selfName, int selfColor, const int pinout) : color(selfColor), pin(pinout){
  status = LOW;
  name  = selfName;
}

Led::Led(): color(-1), pin(-1) {
  name = "";
  status = false;
}

Led:: ~Led() {
}

int Led::getStatus(){
  return this->status;
}

int Led::getColor() {
  return this->color;
}

String Led::getName(){
  return this->name;
}

void Led::changeLedState(String state) {
  if (state.equalsIgnoreCase("ON")) {
    digitalWrite(this->pin, HIGH);
    this->status = HIGH;
  }
  else {
    digitalWrite(this->pin, LOW);
    this->status = LOW;
  }
}
