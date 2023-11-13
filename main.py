/////////--------IOT--------FIAP------------///////////

#include <WiFi.h>
#include <DHTesp.h>
#include <PubSubClient.h>

// Configurações de WiFi
const char *SSID = "Wokwi-GUEST";
const char *PASSWORD = "";  // Substitua pelo sua senha

// Configurações de MQTT
const char *BROKER_MQTT = "46.17.108.113";
const int BROKER_PORT = 1883;
const char *ID_MQTT = "fiware_lamp209";
const char *TOPIC_PUBLISH_TEMP = "/TEF/FarmProVision/attrs/t";
const char *TOPIC_PUBLISH_UMID = "/TEF/FarmProVision/attrs/h";
const char *TOPIC_PUBLISH_LDR = "/TEF/FarmProVision/attrs/l";


// Configurações de Hardware
#define PIN_DHT 12
#define PUBLISH_DELAY 2000
#define PIN_LDR 32  // Pino do sensor LDR
#define PIN_RED_LED 10
#define PIN_GREEN_LED 11
#define PIN_BUZZER 12

// Variáveis globais
WiFiClient espClient;
PubSubClient MQTT(espClient);
DHTesp dht;
unsigned long publishUpdate = 0;
TempAndHumidity sensorValues;

// Protótipos de funções
void updateSensorValues();
void initWiFi();
void initMQTT();
void reconnectMQTT();
void reconnectWiFi();
void checkWiFIAndMQTT();

void updateSensorValues() {
  sensorValues = dht.getTempAndHumidity();
}

void initWiFi() {
  Serial.print("Conectando com a rede: ");
  Serial.println(SSID);
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Conectado com sucesso: ");
  Serial.println(SSID);
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void initMQTT() {
  MQTT.setServer(BROKER_MQTT, BROKER_PORT);
}

void reconnectMQTT() {
  while (!MQTT.connected()) {
    Serial.print("Tentando conectar com o Broker MQTT: ");
    Serial.println(BROKER_MQTT);

    if (MQTT.connect(ID_MQTT)) {
      Serial.println("Conectado ao broker MQTT!");
    } else {
      Serial.println("Falha na conexão com MQTT. Tentando novamente em 2 segundos.");
      delay(2000);
    }
  }
}

void checkWiFIAndMQTT() {
  if (WiFi.status() != WL_CONNECTED) reconnectWiFi();
  if (!MQTT.connected()) reconnectMQTT();
}

void reconnectWiFi(void) {
  if (WiFi.status() == WL_CONNECTED)
    return;

  WiFi.begin(SSID, PASSWORD); // Conecta na rede WI-FI

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Wifi conectado com sucesso");
  Serial.print(SSID);
  Serial.println("IP: ");
  Serial.println(WiFi.localIP());
}


void setup() {
  Serial.begin(115200);
  dht.setup(PIN_DHT, DHTesp::DHT22);
  initWiFi();
  initMQTT();
  pinMode(PIN_RED_LED, OUTPUT);
  pinMode(PIN_GREEN_LED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
}

void loop() {
  checkWiFIAndMQTT();
  MQTT.loop();
  if ((millis() - publishUpdate) >= PUBLISH_DELAY) {
    publishUpdate = millis();
    updateSensorValues();

    // temperatura
    char msgBuffer1[5];
    float sensorValue1 = sensorValues.temperature;
    Serial.print("Temperature: ");
    Serial.println(sensorValue1);
    dtostrf(sensorValue1, 4, 2, msgBuffer1);
    MQTT.publish(TOPIC_PUBLISH_TEMP, msgBuffer1);

    // umidade
    char msgBuffer2[5];
    float sensorValue2 = sensorValues.humidity;
    Serial.print("Humidity: ");
    Serial.println(sensorValue2);
    dtostrf(sensorValue2, 4, 2, msgBuffer2);
    MQTT.publish(TOPIC_PUBLISH_UMID, msgBuffer2);

    // leitura do LDR
    char msgBuffer3[7];  // Ajuste o tamanho do buffer conforme necessário
    int sensorValue3 = analogRead(PIN_LDR);
    Serial.print("LDR: ");
    Serial.println(sensorValue3);
    dtostrf(sensorValue3, 6, 2, msgBuffer3);
    MQTT.publish(TOPIC_PUBLISH_LDR, msgBuffer3);
  }