#ifndef SMARTHOME_WEBSERVER_H
#define SMARTHOME_WEBSERVER_H

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <ArduinoJson.h>
#include <uri/UriRegex.h>

#include "config.h"
#include "peripherals.h"


void setEndpoints();
void wifiSet();
void swichLedEP();
void handleTestInt();
void handleLcd();
void handleAll();
void handleTemp();
void handlePotenionmeter();
void handleNotFound();
void handleRoot();
void serverHandleClient();

#endif