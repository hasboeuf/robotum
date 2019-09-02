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
const char* ROBOT_BOARD_IP = "a.b.c.d";
const int ROBOT_BOARD_PORT = 1024;
const int ROBOT_POWER_DELAY = 20000;
std::vector<int> PINS = {16, 5, 4, 0, 2, 14, 12, 13, 15};
const int ROBOT_POWER_GPIO = 1;
const int BUZZER_GPIO = 2;

const std::string ENDPOINT_ROOT = "^/$";
const std::string ENDPOINT_STATUS = "^/status$";
const std::string ENDPOINT_ROBOT_START = "^/robot/start$";
const std::string ENDPOINT_ROBOT_STOP = "^/robot/stop$";
const std::string ENDPOINT_ROBOT_FORCE_STOP = "^/robot/stop/force$";
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

void buzzKo() {
  int buzz = PINS[BUZZER_GPIO];
  tone(buzz, 370, 50);
  delay(100);
  tone(buzz, 370, 300);
}

void buzzOk() {
  tone(PINS[BUZZER_GPIO], 2093, 100);
}

void buzzOkWifi() {
  int buzz = PINS[BUZZER_GPIO];
  tone(buzz, 523, 50);
  delay(50);
  tone(buzz, 783, 50);
  delay(50);
  tone(buzz, 1046, 50);
  delay(50);
  tone(buzz, 1568, 50);
  delay(50);
  tone(buzz, 2093, 70);
}

Router router;
ESP8266WebServer server(80);
WiFiClient robotSocket;
bool robotPowered = false;
String robotStatus = "DISCONNECTED"; // CONNECTING CONNECTED DISCONNECTING
long lastTimestamp = 0;
long lastConnectedTimestamp = 0;

void sendJson(int httpCode, const JsonDocument& doc) {
  std::string response;
  serializeJsonPretty(doc, response);
  server.send(httpCode, "text/json", response.c_str());
  if (httpCode == 200) {
    buzzOk();
  } else {
    buzzKo();
  }
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
  JsonObject robot = doc.createNestedObject("robot");
  robot["ip"] = ROBOT_BOARD_IP;
  robot["powered"] = robotPowered;
  String poweredFor = "N/A";
  if (robotPowered && robotStatus == "DISCONNECTING") {
    poweredFor = String(lastConnectedTimestamp + ROBOT_POWER_DELAY - millis()) + "ms";
  }
  robot["powered_for"] = poweredFor;
  robot["status"] = robotStatus;
  sendJson(200, doc);
}

void handleRobotStart(std::vector<std::string>) {
  if (robotStatus != "DISCONNECTED") {
    sendNotAllowed("Robot is not DISCONNECTED");
    return;
  }

  StaticJsonDocument<256> doc;
  doc["code"] = "OK";
  doc["message"] = "Starting...";

  robotPowered = true;
  robotStatus = "CONNECTING";

  digitalWrite(PINS[ROBOT_POWER_GPIO], 1);

  sendJson(200, doc);
}

void handleRobotStop(std::vector<std::string>) {
  if (robotStatus != "CONNECTED") {
    sendNotAllowed("Robot is not CONNECTED");
    return;
  }

  StaticJsonDocument<256> doc;
  doc["code"] = "OK";
  doc["message"] = "Stopping...";

  robotStatus = "DISCONNECTING";

  sendJson(200, doc);
}

void handleRobotForceStop(std::vector<std::string>) {
  Serial.println("Turn off power");
  digitalWrite(PINS[ROBOT_POWER_GPIO], 0);

  robotStatus = "DISCONNECTED";
  robotPowered = false;

  StaticJsonDocument<256> doc;
  doc["code"] = "OK";
  doc["message"] = "Stopped.";

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

  pinMode(PINS[ROBOT_POWER_GPIO], OUTPUT);
  digitalWrite(PINS[ROBOT_POWER_GPIO], 0);

  pinMode(PINS[BUZZER_GPIO], OUTPUT);
  digitalWrite(PINS[BUZZER_GPIO], 0);

  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  Serial.println("");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  buzzOkWifi();

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
  router.addRoute(HTTP_PUT, ENDPOINT_ROBOT_START, handleRobotStart);
  router.addRoute(HTTP_PUT, ENDPOINT_ROBOT_STOP, handleRobotStop);
  router.addRoute(HTTP_PUT, ENDPOINT_ROBOT_FORCE_STOP, handleRobotForceStop);
  router.addRoute(HTTP_PUT, ENDPOINT_RESTART, handleRestart);

  server.onNotFound([]() {
    router.handle(server.method(), std::string(server.uri().c_str()));
  });

  server.begin();
  Serial.println("HTTP server started");
}

void loop(void) {
  long currentTimestamp = millis();

  server.handleClient();
  MDNS.update();

  if (currentTimestamp - lastTimestamp > 1000) {
    // Check every second
    lastTimestamp = currentTimestamp;

    if (robotStatus == "CONNECTING") {
      Serial.println("Try to connect the robot...");
      if (!robotSocket.connect(ROBOT_BOARD_IP, ROBOT_BOARD_PORT)) {
        Serial.println("Failed to connect the robot");
      } else {
        Serial.println("Robot connected!");
        robotStatus = "CONNECTED";
        lastConnectedTimestamp = millis();
      }
    }

    if (robotStatus == "CONNECTED") {
      robotSocket.print("ping\n");
      robotSocket.flush();

      long timeout = millis() + 2000;
      bool received = false;
      while (!received && millis() < timeout) {
        received = robotSocket.available();
        delay(200);
      }

      if (!received) {
        Serial.println("Robot timeout! (did not receive PONG in time)");
        robotSocket.stop();
        robotStatus = "CONNECTING";
        return;
      }

      String buffer = robotSocket.readStringUntil('\n');
      if (buffer == "pong") {

      } else {
        Serial.print("Received unknown message: ");
        Serial.println(buffer);
      }

      lastConnectedTimestamp = millis();
    }

    if (robotStatus == "DISCONNECTING" && robotSocket.connected()) {
      Serial.println("Send shutdown order");
      robotSocket.print("shutdown\n");
      robotSocket.flush();
    }

    if (robotStatus == "DISCONNECTING" && currentTimestamp - lastConnectedTimestamp > ROBOT_POWER_DELAY) {
      Serial.println("Turn off power");
      digitalWrite(PINS[ROBOT_POWER_GPIO], 0);
      robotPowered = false;
      robotStatus = "DISCONNECTED";
    }
  }
}
