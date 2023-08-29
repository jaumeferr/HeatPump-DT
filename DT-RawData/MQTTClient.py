from paho.mqtt import client as mqttClient


class MQTTClient():
    def __init__(self, broker, port):
        self.clientId = "mosquitto_client_01"
        self.broker = broker
        self.port = port
        self.user = "jfm174"
        self.password = "password"

    def openMQTT(self):
        self.mqtt = mqttClient.Client(self.clientId)

        self.mqtt.on_connect = self.onConnect
        self.mqtt.on_message = self.onMessage

        self.mqtt.connect(self.broker, port=self.port, keepalive=65)
        self.mqtt.loop_start()

        return self.mqtt

    def onConnect(self, client, userdata, flags, rc):
        self.mqtt.subscribe("plc_control")
        print("Connection ACK: " + str(rc))

    # Comunicación physical twin --> digital twin:  Publicación del registro de actividad en el broker
    def updateValues(self, msg):
        r = self.mqtt.publish("sensor_values", msg)
        if r[0] == 0:
            print("Message sent successfully")
        else:
            print("Failed to send message")

    # Comunicación digital twin --> physical twin
    def onMessage(self, client, userdata, msg):
        print("Soon")