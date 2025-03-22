#include "Led.h"

Led::Led(char* selfName, int selfColor, const int pinout) : color(selfColor), pin(pinout){
  status = LOW;
  name  = new char[strlen(selfName)+1];
  strcpy(name, selfName);
}

Led::Led(): color(-1), pin(-1) {
  name = nullptr;
  status = false;
}

Led:: ~Led() {
  delete[] name;
}

int Led::getStatus(){
  return this->status;
}

int Led::getColor() {
  return this->color;
}

char* Led::getName(){
  return this->name;
}

void Led::changeLedState() {
  digitalWrite(this->pin, !(this->status));
  this->status = !(this->status);
}
