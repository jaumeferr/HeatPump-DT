from flask import Flask, request, jsonify, json
from flask_cors import CORS
from Constants import Constants
from paho.mqtt import client as mqttClient
from DBA.MongoDBA import MongoDBA
from Services.Decider import Decider
from Services.Modelation import Modelation
from Services.Simulation import Simulation
from datetime import datetime


##########   Flask Server Init   ##########
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False


##########   Incializar conex. BBDD   ##########
dba = MongoDBA()

##########   Incilizar módulos de servicio   ##########
constants = Constants() # constantes de la bomba de calor
dt_decider = Decider(dba, constants) # decididor
dt_modelation = Modelation(dba, constants) # modelado
dt_simulation = Simulation(dba, constants) # simulador


##########   Inicializar conex. con Mosquitto   ##########
mqtt_broker = "192.168.1.64" #IP de la VM que aloja el servidor Mosquitto
mqtt_port = 1883
mqtt_client_id = "mosquitto_client_02"
mqtt_user = "jfm174"
mqtt_password = "password"

def onConnect(client, userdata, flags, rc):
    print("Connection ACK: " + str(rc))
    mqtt.subscribe("sensor_values")


def onMessage(client, userdata, msg):
    data = json.loads(str(msg.payload.decode("utf-8")))
    dba.postSensorValues(data)

    new_alerts = dt_decider.checkStatus(data)
    dt_decider.updateActiveAlerts(new_alerts)
    print(dt_decider.active_alerts)

    dt_decider.checkEventsFromNewData(data)
    print(dt_decider.last_events)

# Set params
mqtt = mqttClient.Client(mqtt_client_id)
mqtt.on_connect = onConnect
mqtt.on_message = onMessage
mqtt.loop_start()
mqtt.connect(mqtt_broker, port=mqtt_port, keepalive=65) # conectar con Mosquitto


##########   Interacción con el cliente   ##########

# Obtener valores más recientes almacenados en BBDD
@app.route('/sensor_values', methods=['GET'])
def getLastValues():
    res = dba.getLastSensorValues()
    if(res):
        return json.dumps(dt_decider.formatDataToString(res))

# Obtener mensajes de alerta activos
@app.route('/alerts', methods=['GET'])
def getAlerts():
    print("Envío de alertas a cliente")
    return json.dumps(dt_decider.active_alerts)

# Obtener estado general del sistema (ON/OFF - Temperat. Consigna)
@app.route('/status', methods=['GET'])
def getSystemStatus():
    res = dt_decider.getSystemStatus()

    if res:
        return json.dumps(dt_decider.formSystemStatus(res))

# Obtener listado de últimos eventos del sistema
@app.route('/events', methods=['GET','POST'])
def getEvents():
    return json.dumps(dt_decider.last_events)

# Obtener constantes del sistema
@app.route('/constants', methods=['GET'])
def getConstantValues():
    cons = Constants()
    var_names = list(cons.__dict__.keys())
    var_values = []
    for name in var_names:
        var_values.append(getattr(cons, name))

    return json.dumps(dict(zip(var_names, var_values)))

# Programacion de arranque inteligente
@app.route('/predict_boot', methods=['POST'])
def predictBoot():
    data = request.form['data']
    data = json.loads(data)

    # Actualizar lista de eventos
    dt_decider.pushEventFromClient(data)

    res = dt_simulation.startNewSimulation(data, dt_decider.consigTemp)
    return json.dumps(dt_decider.last_events) # Devuelve el listado de eventos para confirmar arranque

@app.route('/boot', methods=['GET']) # Esta ruta tiene carácter interno y solo es visible para el lado servidor
def boot():
    curr_time = dba.getLastSensorValues()
    curr_time = curr_time['Datetime']
    dt_decider.pushEvent({"datetime": curr_time, "type": "Sistema",
                          "msg": "El sistema se ha encendido"}) # Crear evento de sistema para simular arranque
    return "0"

app.run()