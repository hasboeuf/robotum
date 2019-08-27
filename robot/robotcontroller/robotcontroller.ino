#define ARDUINOJSON_ENABLE_STD_STRING 1

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ArduinoJson.h>
#include <Regexp.h>
#include <vector>
#include <list>
#include <map>

const char* SSID = "SSID";
const char* PASSWORD = "PASSWORD";

std::vector<int> PINS = {16, 5, 4, 0, 2, 14, 12, 13, 15};
std::vector<int> CACHE_VALUES = {-1, -1, -1, -1, -1, -1, -1, -1, -1};

const std::string ENDPOINT_ROOT = "^/$";
const std::string ENDPOINT_STATUS = "^/status$";
const std::string ENDPOINT_GPIO_LIST = "^/gpio$";
const std::string ENDPOINT_GPIO_LIST_ONE = "^/gpio/(%d+)$";
const std::string ENDPOINT_GPIO_SET_VALUE = "^/gpio/(%d+)/value/(%a+)$";
const std::string ENDPOINT_GPIO_SET_MODE = "^/gpio/(%d+)/mode/(%a+)$";
const std::string ENDPOINT_RESTART = "^/restart$";


class Route {
  public:
    using Callback = std::function<void (std::vector<std::string>)>;
    enum HandleCode {
      HANDLE_OK,
      HANDLE_WRONG_URL,
      HANDLE_WRONG_METHOD
    };

    Route(std::string url) {
      mUrl = url;
    }

    void addCallback(HTTPMethod method, Callback callback) {
      mCallbacks[method] = callback;
    }

    HandleCode handle(HTTPMethod method, std::string path) {
      MatchState ms;
      ms.Target((char*) path.c_str());
      char result = ms.Match((char*) mUrl.c_str());
      if (result != REGEXP_MATCHED) {
        return HANDLE_WRONG_URL;
      }

      if (!mCallbacks.count(method)) {
        return HANDLE_WRONG_METHOD;
      }

      std::vector<std::string> args;
      args.push_back(path);

      for (int i = 0; i < ms.level; ++i) {
        char buffer[100] = {0};
        ms.GetCapture (buffer, i);
        args.push_back(buffer);
      }

      mCallbacks[method](args);
      return HANDLE_OK;
    }

  private:
    std::string mUrl;
    std::map<HTTPMethod, Callback> mCallbacks;
};


class Router {
  public:
    using Callback = std::function<void ()>;
    void addRoute(HTTPMethod method, std::string url, Route::Callback callback) {
      if (url.size() == 0) {
        return;
      }

      Route* route;
      if (mRoutes.count(url)) {
        route = mRoutes[url];
      } else {
        route = new Route(url);
        mRoutes[url] = route;
      }
      route->addCallback(method, callback);

      std::string endpoint = stringForHTTPMethod(method) + " " + url;
      Serial.print("Added ");
      Serial.println(endpoint.c_str());
      mEndpoints.push_back(endpoint);
    }

    void setNotFoundCallback(Callback callback) {
      mNotFoundCallback = callback;
    }

    void setNotPermittedCallback(Callback callback) {
      mNotPermittedCallback = callback;
    }

    std::list<std::string> endpoints() const {
      return mEndpoints;
    }

    void handle(HTTPMethod method, std::string path) {
      Serial.print("Received ");
      Serial.print(stringForHTTPMethod(method).c_str());
      Serial.print(" ");
      Serial.println(path.c_str());

      Route::HandleCode result = Route::HANDLE_WRONG_URL;
      Route* route = nullptr;
      std::map<std::string, Route*>::const_iterator it = mRoutes.cbegin();
      while (it != mRoutes.cend() && result == Route::HANDLE_WRONG_URL) {
        ESP.wdtFeed(); // https://techtutorialsx.com/2017/01/21/esp8266-watchdog-functions/
        route = it->second;
        ++it;
        result = route->handle(method, path);
      }

      if (result == Route::HANDLE_WRONG_METHOD) {
        Serial.println("Not permitted");
        if (mNotPermittedCallback) {
          mNotPermittedCallback();
        }
      } else if (result == Route::HANDLE_WRONG_URL) {
        Serial.println("Not found");
        if (mNotFoundCallback) {
          mNotFoundCallback();
        }
      }
    }

  private:
    std::string stringForHTTPMethod(HTTPMethod method) {
      switch (method) {
        case HTTP_ANY:
          return "ANY";
        case HTTP_GET:
          return "GET";
        case HTTP_POST:
          return "POST";
        case HTTP_PUT:
          return "PUT";
        case HTTP_PATCH:
          return "PATCH";
        case HTTP_DELETE:
          return "DELETE";
        default:
          return "OPTIONS";
      }
    }

    std::map<std::string, Route*> mRoutes;
    Callback mNotFoundCallback;
    Callback mNotPermittedCallback;
    std::list<std::string> mEndpoints;
};

std::string pinMode(unsigned int pin)
{
  if (pin >= PINS.size()) {
    return "";
  }

  uint32_t bit = digitalPinToBitMask(PINS[pin]);
  uint32_t port = digitalPinToPort(PINS[pin]);
  volatile uint32_t* reg = portModeRegister(port);
  if (*reg & bit) {
    return "OUTPUT";
  }

  volatile uint32_t* out = portOutputRegister(port);
  return ((*out & bit) ? "INPUT_PULLUP" : "INPUT");
}

int readPinValue(int pin) {
  std::string mode = pinMode(pin);
  if (mode == "" || mode == "OUTPUT") {
    return -1;
  }
  return digitalRead(PINS[pin]);
}

Router router;
ESP8266WebServer server(80);

void sendJson(int httpCode, const JsonDocument& doc) {
  std::string response;
  serializeJsonPretty(doc, response);
  server.send(httpCode, "text/json", response.c_str());
}

void sendNotAllowed(std::string message) {
  StaticJsonDocument<256> doc;
  doc["code"] = "NOT_ALLOWED";
  doc["message"] = message;
  sendJson(405, doc);
}

void handleNotAllowed() {
  sendNotAllowed("Action not allowed");
}

void handleNotFound() {
  StaticJsonDocument<256> doc;
  doc["code"] = "NOT_FOUND";
  doc["message"] = "Wrong API endpoint";
  sendJson(404, doc);
}

void handleRoot(std::vector<std::string>) {
  StaticJsonDocument<512> doc;
  JsonArray endpoints = doc.createNestedArray("endpoints");
  for (const std::string& endpoint : router.endpoints()) {
    endpoints.add(endpoint);
  }
  sendJson(200, doc);
}

void handleStatus(std::vector<std::string>) {
  StaticJsonDocument<256> doc;
  doc["code"] = "OK";
  doc["message"] = "Up and running";
  doc["signal"] = WiFi.RSSI();
  sendJson(200, doc);
}

void handleGpioList(std::vector<std::string>) {
  StaticJsonDocument<1024> doc;
  JsonArray gpios = doc.createNestedArray("gpios");
  for (unsigned int i = 0; i < PINS.size(); ++i) {
    JsonObject gpio = gpios.createNestedObject();
    gpio["id"] = i;
    gpio["internal_id"] = PINS[i];
    gpio["mode"] = pinMode(i);
    gpio["value"] = readPinValue(i);
    gpio["cache_value"] = CACHE_VALUES[i];
  }
  sendJson(200, doc);
}

void handleGpioListOne(std::vector<std::string> args) {
  unsigned int id = atoi(args[1].c_str());
  StaticJsonDocument<256> doc;
  if (id >= PINS.size()) {
    sendNotAllowed("Pin not found");
    return;
  }

  doc["id"] = id;
  doc["internal_id"] = PINS[id];
  doc["mode"] = pinMode(id);
  doc["value"] = readPinValue(id);
  doc["cache_value"] = CACHE_VALUES[id];
  sendJson(200, doc);
}

void handleGpioSetValue(std::vector<std::string> args) {
  unsigned int id = atoi(args[1].c_str());
  int value = args[2] == "low" ? 0 : args[2] == "high" ? 1 : -1;
  StaticJsonDocument<256> doc;

  if (id >= PINS.size()) {
    sendNotAllowed("Pin not found");
    return;
  }

  if (value == -1) {
    sendNotAllowed("Wrong value, should be low|high");
    return;
  }

  if (pinMode(id) != "OUTPUT") {
    sendNotAllowed("Pin not in OUTPUT mode");
    return;
  }

  CACHE_VALUES[id] = value;
  digitalWrite(PINS[id], value);
  std::string msg = "Set " + args[2] + " to GPIO " + args[1];
  doc["code"] = "OK";
  doc["message"] = msg;
  sendJson(200, doc);
}

void handleGpioSetMode(std::vector<std::string> args) {
  unsigned int id = atoi(args[1].c_str());
  std::string mode = args[2];
  StaticJsonDocument<256> doc;

  if (id >= PINS.size()) {
    sendNotAllowed("Pin not found");
    return;
  }

  if (mode != "input" && mode != "output") {
    sendNotAllowed("Unknown mode, should be input|output");
    return;
  }

  if (mode == "input") {
    pinMode(PINS[id], INPUT);
  } else {
    pinMode(PINS[id], OUTPUT);
  }

  std::string msg = "Set " + args[1] + " to mode " + mode;
  doc["code"] = "OK";
  doc["message"] = msg;
  sendJson(200, doc);
}

void handleRestart(std::vector<std::string>) {
  StaticJsonDocument<256> doc;
  doc["code"] = "OK";
  doc["message"] = "Restarting...";
  sendJson(200, doc);
  delay(2000);
  ESP.restart();
}

void setup(void) {
  Serial.begin(9600);

  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  Serial.println("");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(SSID);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }

  router.setNotFoundCallback(handleNotFound);
  router.setNotPermittedCallback(handleNotAllowed);
  router.addRoute(HTTP_GET, ENDPOINT_ROOT, handleRoot);
  router.addRoute(HTTP_GET, ENDPOINT_STATUS, handleStatus);
  router.addRoute(HTTP_GET, ENDPOINT_GPIO_LIST, handleGpioList);
  router.addRoute(HTTP_GET, ENDPOINT_GPIO_LIST_ONE, handleGpioListOne);
  router.addRoute(HTTP_PUT, ENDPOINT_GPIO_SET_VALUE, handleGpioSetValue);
  router.addRoute(HTTP_PUT, ENDPOINT_GPIO_SET_MODE, handleGpioSetMode);
  router.addRoute(HTTP_PUT, ENDPOINT_RESTART, handleRestart);

  server.onNotFound([]() {
    router.handle(server.method(), std::string(server.uri().c_str()));
  });

  server.begin();
  Serial.println("HTTP server started");
}

void loop(void) {
  server.handleClient();
  MDNS.update();
}
