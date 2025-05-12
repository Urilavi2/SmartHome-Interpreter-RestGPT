#include "homewebserver.h"

WebServer server(80);
String ssid = SSID_NAME;
String password = SSID_PASS;


void swichLedEP() {
  if ((server.hasArg("color")) && (server.hasArg("state"))) {
    String color, state, tmp; 
    JsonDocument doc;
    int ledStatus, ledId;

    color = server.arg("color");
    state = server.arg("state");

    if (!(state.equalsIgnoreCase("ON")) && !(state.equalsIgnoreCase("OFF"))) {
      handleNotFound();
      return;
    }

    ledId = getLedIdByName(color);
    if (ledId == -1) {
      handleNotFound();
      return;
    }

    ledStatus = switchLed(ledId, state);
    if (ledStatus == -1) {
      handleNotFound();
      return;
    }
    doc["color"] = color;
    if (ledStatus)
      doc["status"] = "ON";
    else
      doc["status"] = "OFF";
    serializeJson(doc, tmp);
    server.send(200, APP_JSON, tmp);

  }
  else {
    handleNotFound();
    return;
  }
}

void ledStatus() {
  if  (!server.hasArg("color")){
    handleNotFound();
    return;
  }
  String color, tmp; 
  JsonDocument doc;
  int status, ledId;

  color = server.arg("color");
  ledId = getLedIdByName(color);
  if (ledId == -1) {
    handleNotFound();
    return;
  }
  status = getLedStatus(ledId);
  
  doc["color"] = color;
  if (status){
    doc["status"] = "ON";
  }
  else {
    doc["status"] = "OFF";
  }

  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handleToggleLed() {
  String pathVar = server.pathArg(0);
  String tmp;
  JsonDocument doc;
  doc[KEY_MSG] = pathVar;
  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handleLcd() {
  JsonDocument doc_body;
  String tmp;
  String body = server.arg("plain");
  deserializeJson(doc_body, body);
  if (doc_body["message"].is<String>()) {  // Check if JSON holds "message" key
    String msg = doc_body["message"];
    writeLCD(msg);
    deserializeJson(doc_body, tmp);
    doc_body["message"] = msg;
    serializeJson(doc_body, tmp);
    server.send(200, APP_JSON, tmp);
  } else {
    deserializeJson(doc_body, tmp);
    doc_body["message"] = "Bad request";
    serializeJson(doc_body, tmp);
    server.send(400, APP_JSON, tmp);
  }
}

void getLcd() {
  JsonDocument doc;
  String tmp;
  doc["message"] = readLCD();
  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handleAll() {
  JsonDocument doc;
  String tmp;
  int status;
  JsonArray ledArr = doc["led"].to<JsonArray>();
  for (int i=0;i<getLedsSize();i++){
    JsonDocument tempDoc;
    tempDoc["color"] = getLed(i)->getName();
    status = getLedStatus(i);
    if (status != -1) {
      if (status)
          tempDoc["status"] = "ON";
      else
        tempDoc["status"] = "OFF";
    }
    else {
      tempDoc["status"] = "Not Found!";
    }
    ledArr.add(tempDoc);
  }

  JsonObject lcd = doc["lcd"].to<JsonObject>();
  lcd["message"] = readLCD();

  JsonObject tempature = doc["tempature"].to<JsonObject>();
  tempature["farhenheit"] = getTemperature(false);
  tempature["celsius"] = getTemperature(true);

  JsonObject potentiometer = doc["potentiometer"].to<JsonObject>();
  potentiometer["resistance"] = getPotentiometer();
  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handleTemp() {
  JsonDocument doc;
  String tmp;
  doc["farhenheit"] = getTemperature(false);
  doc["celsius"] = getTemperature(true);
  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handlePotenionmeter() {
  JsonDocument doc;
  String tmp;
  doc["resistance"] = getPotentiometer();
  serializeJson(doc, tmp);
  server.send(200, APP_JSON, tmp);
}

void handleNotFound() {
  JsonDocument doc;
  String tmp;
  String message = "Path Not Found | ";
  message += "URI: ";
  message += server.uri();
  message += " | Method: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\ | Arguments: ";
  message += server.args();
  message += " | ";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + " | ";
  }
  doc[KEY_MSG] = message;
  serializeJson(doc, tmp);
  server.send(404, APP_JSON, tmp);
}

void handleRoot() {
  server.send(200, "text/plain", "Hello World!");
}

void wifiSet() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("");
  Serial.print("\nConnected to:\n");
  Serial.println(ssid);
  Serial.print("IP address:\n");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("api-esp32-smarthome")) {
    Serial.println("MDNS responder started");
  }
  server.begin();
}


void setEndpoints() {
  server.onNotFound(handleNotFound);
  server.on("/led", HTTP_GET, swichLedEP);
  server.on("/led-status", HTTP_GET, ledStatus);
  server.on("/led/toggle", HTTP_GET, handleToggleLed);
  server.on("/lcd", HTTP_POST, handleLcd);
  server.on("/lcd", HTTP_GET, getLcd);
  server.on("/get-all", HTTP_GET, handleAll);
  server.on("/temperature", HTTP_GET, handleTemp);
  server.on("/potentiometer", HTTP_GET, handlePotenionmeter);
  server.on("/", HTTP_GET, handleRoot);
}

void serverHandleClient() {
  server.handleClient();
}
