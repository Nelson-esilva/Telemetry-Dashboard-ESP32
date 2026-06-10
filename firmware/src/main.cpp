#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

static unsigned long lastSendMs = 0;
static int pecasProduzidas = 0;

static const char *STATUS_RUNNING = "RUNNING";
static const char *STATUS_IDLE = "IDLE";
static const char *STATUS_ALARM = "ALARM";

void connectWiFi() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }

    Serial.print("Conectando ao WiFi: ");
    Serial.println(WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("WiFi conectado. IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("Falha ao conectar ao WiFi.");
    }
}

float randomFloat(float minVal, float maxVal) {
    return minVal + (static_cast<float>(random(0, 10001)) / 10000.0f) * (maxVal - minVal);
}

const char *pickStatus() {
    int roll = random(0, 100);
    if (roll < 85) {
        return STATUS_RUNNING;
    }
    if (roll < 95) {
        return STATUS_IDLE;
    }
    return STATUS_ALARM;
}

bool sendTelemetry() {
    pecasProduzidas += random(0, 4);

    float temperatura = randomFloat(25.0f, 75.0f);
    int rpm = random(800, 1501);
    const char *status = pickStatus();
    float tempoCiclo = randomFloat(1.5f, 4.0f);
    float eficiencia = randomFloat(85.0f, 99.0f);

    JsonDocument doc;
    doc["device_id"] = DEVICE_ID;
    doc["pecas_produzidas"] = pecasProduzidas;
    doc["temperatura_c"] = round(temperatura * 10.0f) / 10.0f;
    doc["rpm_motor"] = rpm;
    doc["status_maquina"] = status;
    doc["tempo_ciclo_s"] = round(tempoCiclo * 10.0f) / 10.0f;
    doc["eficiencia_pct"] = round(eficiencia * 10.0f) / 10.0f;

    String payload;
    serializeJson(doc, payload);

    String url = String("http://") + API_HOST + ":" + String(API_PORT) + "/telemetry";
    Serial.print("Enviando para ");
    Serial.println(url);
    Serial.println(payload);

    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(payload);
    if (httpCode > 0) {
        Serial.print("Resposta HTTP: ");
        Serial.println(httpCode);
        if (httpCode >= 200 && httpCode < 300) {
            http.end();
            return true;
        }
    } else {
        Serial.print("Erro HTTP: ");
        Serial.println(http.errorToString(httpCode));
    }

    http.end();
    return false;
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    randomSeed(analogRead(0));

    Serial.println("=== Telemetria de Producao - ESP32 ===");
    connectWiFi();
}

void loop() {
    connectWiFi();

    unsigned long now = millis();
    if (now - lastSendMs >= TELEMETRY_INTERVAL_MS) {
        lastSendMs = now;

        if (WiFi.status() == WL_CONNECTED) {
            if (!sendTelemetry()) {
                Serial.println("Falha no envio. Tentando reconectar WiFi...");
                WiFi.disconnect();
                delay(1000);
                connectWiFi();
            }
        } else {
            Serial.println("WiFi desconectado. Reconectando...");
            connectWiFi();
        }
    }

    delay(100);
}
