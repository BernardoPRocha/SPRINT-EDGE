from flask import Flask, render_template
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# Configurações MQTT
broker_url = "46.17.108.113"
broker_port = 1883
topics = [
    "/TEF/FarmProVision/attrs/t",
    "/TEF/FarmProVision/attrs/h",
    "/TEF/FarmProVision/attrs/l"
]

temperatura_data = "N/A"
umidade_data = "N/A"
luminosidade_data = "N/A"

# Callback de conexão MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conexão ao broker MQTT bem-sucedida")
        for topic in topics:
            client.subscribe(topic)
    else:
        print("Falha na conexão ao broker MQTT")

# Callback para receber mensagens MQTT
def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    global temperatura_data, umidade_data, luminosidade_data
    if topic == "/TEF/FarmProVision/attrs/t":
        temperatura_data = payload
    elif topic == "/TEF/FarmProVision/attrs/h":
        umidade_data = payload
    elif topic == "/TEF/FarmProVision/attrs/l":
        luminosidade_data = payload

# Configuração do cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_url, broker_port, 60)

# Função para rodar o loop MQTT
def mqtt_loop():
    client.loop_start()

# Inicie o loop MQTT em uma thread
mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

# Rota para a página HTML
@app.route('/')
def dashboard():
    return render_template('dashboard.html', temperatura=temperatura_data, umidade=umidade_data, luminosidade=luminosidade_data)

if __name__ == '__main__':
    app.run(debug=True)
