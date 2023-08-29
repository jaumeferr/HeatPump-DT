import time
import pickle
import threading
from datetime import datetime, timedelta
import pandas as pd
import requests
from pymongo import MongoClient


class Simulation:
    def __init__(self, dba, constants):
        self.dba = dba
        self.constants = constants
        self.threads = []

        # Init. información de la BBDD secundaria que contiene predicciones meteorológicas
        self.weather_DB = 'weatherDB'
        self.weatherDB_COL = 'historicalCOL'
        self.sim_time = None

        # Nombre del modelo almacenado en local por el servicio de modelado
        self.filename = 'model.pkl'

# Predicción de la viabilidad del arranque de la bomba
    def predictBootConditions(self, curr_time, sch_time, curr_temp, curr_water_temp, predicted_temp, sch_consig_temp):
        headers = ['Temperatura aigua impuls', 'Temperatura consigna', 'Temperatura exterior (AEMET)', 'Temperatura exterior (esperada)']

        #Cargar modelo generador por el Modelador
        autoBootModel = pickle.load(open(self.filename, 'rb'))

        #Predicción a partir del modelo
        if autoBootModel:
            temp_impuls = (float(curr_water_temp.replace(',', ".")))
            temp_consigna = sch_consig_temp
            temp_exterior = (float(curr_temp.replace(',', ".")))
            temp_exterior_pred = (float(predicted_temp.replace(',', ".")))

            x = dict(zip(headers, [[temp_impuls], [temp_consigna], [temp_exterior], [temp_exterior_pred]]))
            x = pd.DataFrame.from_dict(x)
            y = autoBootModel.predict(x)[0]

            # Comprobación de las condiciones de arranque
            sch_time_obj = datetime.strptime(sch_time + ":00+0100", '%Y-%m-%dT%H:%M:%S%z')
            curr_time_obj = datetime.strptime(curr_time, '%Y-%m-%dT%H:%M:%S%z')

            time_diff = self.datetimeDiffInMinutes(curr_time_obj, sch_time_obj)
            est_time_proj = self.datetimeDiffInMinutes(curr_time_obj, sch_time_obj - timedelta(minutes=y))

            print("Tiempo estimado para el arranque: " + str(est_time_proj))

            # La bomba arranca asi el tiempo predecido para alcanzar la temperatura consignada es mayor a la
            # diferencia entre la hora actual y la hora establecida
            if y >= time_diff:
                return 1

            # La bomba arrancará también si se supera la hora establecida
            if curr_time_obj > sch_time_obj:
                return 1

            return 0

# Ejecución del método de predicción de arranque en segundo plano
    def startNewSimulation(self, data, consigTemp):
        t = threading.Thread(target=self.predictBoot, args=(data, consigTemp))
        t.start()
        return 1

# Método principal de la predicción de arranque
    def predictBoot(self, data, consigTemp):
        start = 0
        while start == 0:
            values = self.dba.getLastSensorValues()
            values = self.formatDataToString(values)

    # Se definen los parámetros necesarios para predecir el arranque
            curr_temp = values['Temperatura exterior (AEMET)'].replace(',', ".") # Temperatura exterior actual
            curr_water_temp = values['Temperatura aigua impuls'] # Temperatura de actual de salida del tanque
            curr_time = values['Datetime'] # Fecha/Hora del evento (en intervalos de 15 minutos)
            sch_time = data["params"] # Hora programada de entrada del usuario en la casa
            predicted_temp = self.getPredictedTemp(sch_time) # Temperatura predecida para la hora de entrada programada
            sch_consig_temp = consigTemp # Temperatura de salida del tanque a alcanzar a la hora de entrada del usuario

            start = self.predictBootConditions(curr_time, sch_time, curr_temp, curr_water_temp, predicted_temp, sch_consig_temp)

            # Comprueba la viabilidad del arranque cada X tiempo
            if start == 0:
                time.sleep(20)

        self.confirmBoot()

# Diferencia de tiempo entre dos objetos datetime en horas
    def datetimeDiffInHours(self, curr_time_obj, sch_time_obj):
        #Hay que aproximar la fecha y hora a la hora en punto más cercana
        if curr_time_obj.minute >= 30:
            curr_time_obj = curr_time_obj + datetime.timedelta(hours=1)
        curr_time_obj = curr_time_obj.replace(minute=0, second=0)

        if sch_time_obj.minute >= 30:
            sch_time_obj = sch_time_obj + datetime.timedelta(hours = 1)
        sch_time_obj = sch_time_obj.replace(minute=0, second=0)
        
        # Calcular diferencia de horas
        diff = sch_time_obj - curr_time_obj 
        diff_seconds = diff.total_seconds() # Diferencia de horas en segundos
        return divmod(diff_seconds, 3600)[0] #Diferencia de horas en horas

# Diferencia de tiempo entre dos objetos datetime en minutos
    def datetimeDiffInMinutes(self, curr_time_obj, sch_time_obj):
        diff = sch_time_obj - curr_time_obj
        diff_seconds = diff.total_seconds()  # Diferencia de horas en segundos
        return divmod(diff_seconds, 60)[0]  # Diferencia de horas en horas

# Formatar registro a string
    def formatDataToString(self, data):
        for value in data:
            if(isinstance(data[value], str)==False):
                data[value]=str(data[value])
        return data

# Predecir temperatura exterior para la hora de entrada establecida a partir de una BBDD secundaria que permite obtener
# información meteorológica posterior en el tiempo a la fecha actual de la simulación.
    def getPredictedTemp(self, sch_time):

        # Inicializar conex. con BBDD secundaria
        host = 'localhost'
        port = 27017
        con = MongoClient(host, port)
        db = con[self.weather_DB]
        col = db[self.weatherDB_COL]

        # Obtener temperatura exterior para la fecha/hora de entrada programada
        sch_time= sch_time + ":00+0100"
        output = col.find_one({'Datetime': sch_time})
        output = self.formatDataToString(output)
        con.close()
        return output['Temperatura exterior (AEMET)']

# Confirma el arranque y lo notifica al controlador del DT a través de la ruta /boot
    def confirmBoot(self):
        r = requests.get('http://127.0.0.1:5000//boot')
        print(r.status_code)