from datetime import datetime

class Decider:

    def __init__(self, dba, constants):
        self.dba = dba
        self.constants = constants

        # Lista de alertas activas
        self.alert_headers = ['datetime', 'alert_desc']
        self.active_alerts = self.getNewestAlerts(None)

        # Listas de últimos eventos del sistema
        self.last_events = []
        self.max_events = 7 
        
        #Valores de estado general del sistema
        self.system_status_headers = ['status', 'consigTemp'] # Valor ON/OFF y Temperatura consignada
        self.status = 0 # ON --> 1 , OFF --> 0
        self.consigTemp = "55" # En este entorno es constante

        #Configuración de autoarranque
        self.boot_prediction_time = "" #Hora de arranque programada

# Obtener estado general del sistema
    def getSystemStatus(self):
        return [self.status, self.consigTemp]

# Formatar estado generar del sistema a dict
    def formSystemStatus (self, status):
        return dict(zip(self.system_status_headers, status))


# Obtener alertas más recientes según los últimos registros de la bomba
    def getNewestAlerts(self, data):

        # Caso 1 - se quieren obtener alertas a partir de los registros obtenidos en tiempo real
        if data:
            return self.checkStatus(data)

        # Caso 2 - se quiere obtener a partir de los últimos registros almacenados en la BBDD
        else:
            last_values = self.dba.getLastSensorValues()
            if last_values != None:
                # Comprobar alertas a partir de los últimos registros
                return self.checkStatus(last_values)
            else:
                # No hay registros de actividad en el módulo de almacenamiento
                return []

    # Modificar la lista de alertas activas manteniendo la fecha/hora de detección de las todavía vigentes
    def updateActiveAlerts(self, newest_alerts):
        updated_alerts = []

        #Mantener las alertas antiguas que siguen activas
        for active_alert in self.active_alerts:
            for newest_alert in newest_alerts:
                if active_alert['alert_desc']==newest_alert['alert_desc']:
                    updated_alerts.append(active_alert)

        #Insertar las alertas que antes no existían
        updated_alerts_aux = updated_alerts
        for newest_alert in newest_alerts:
            exists = False
            for updated_alert_aux in updated_alerts_aux:
                if newest_alert['alert_desc'] == updated_alert_aux['alert_desc']:
                    exists = True

            if exists == False:
                updated_alerts.append(newest_alert)

        self.active_alerts = updated_alerts

# Notificar el incumplimiento de las leyes estáticas del sistema a partir de los registros de actividad de los sensores
    def checkStatus(self, data):
        new_alerts = [] # [ { datetime: "---" , alert_desc: "---" }, {...}, {...} ]
        data = self.formatDataToString(data)
        if(data):
            if(float(data['Bomba de calor'].replace(',',".")) == 0):
                new_alerts.append(self.formAlert(data['Datetime'], 'no_tension'))

            if (float(data['Bomba de calor'].replace(',', ".")) > self.constants.HE_OUT_MAX_INPUT_POWER):
                new_alerts.append(self.formAlert(data['Datetime'], 'max_potencia'))

            if(float(data['Temperatura aigua impuls'].replace(',',"."))<float(data['Temperatura aigua retorn'].replace(',',"."))): # CONVIENE CAMBIAR NOMBRE A IMPULSO < RETORNO
                new_alerts.append(self.formAlert(data['Datetime'], 'impulso_frio'))

            if(float(data['Temperatura aigua impuls'].replace(',',"."))>float(data['Temperatura consigna'].replace(',',"."))):
                new_alerts.append(self.formAlert(data['Datetime'], 'sobrecalentamiento_tanque'))

            if(float(data['Temperatura exterior (AEMET)'].replace(',',"."))<-20):
                new_alerts.append(self.formAlert(data['Datetime'], 'exterior_frio'))

            if(float(data['Temperatura exterior (AEMET)'].replace(',',"."))>35):
                new_alerts.append(self.formAlert(data['Datetime'], 'exterior_caliente'))

            if (float(data['Temperatura aigua impuls'].replace(',',".")) < 20):
                new_alerts.append(self.formAlert(data['Datetime'], 'tanque_frio'))

            if (float(data['Temperatura aigua impuls'].replace(',',".")) > 55):
                new_alerts.append(self.formAlert(data['Datetime'], 'tanque_caliente'))

        return new_alerts

# Formatar alerta a dict
    def formAlert(self, datetime, desc):
        return dict(zip(self.alert_headers, [datetime, desc]))

# Formatar valor de cadena dict a string
    def formatDataToString(self, data):
        for value in data:
            if(isinstance(data[value], str)==False):
                data[value]=str(data[value])
        return data

# Registrar un evento de sistema
    def pushEvent(self, my_event):
        if(len(self.last_events)==self.max_events):
            #Borrar evento más viejo
            self.last_events.pop(0)
        
        self.last_events.append(my_event)

# Reconocer eventos de sistemas a partir del registro de actividad de los sensores en tiempo real
    def checkEventsFromNewData(self, data):
        self.consigTemp = float(data['Temperatura consigna'].replace(',',"."))

        if((float(data['Bomba de calor'].replace(',',".")) > 0.15) and (self.status==0) ):
            self.pushEvent({"datetime": data['Datetime'], "type":"Sistema", "msg": "El sistema se ha encendido"})
            self.status = 1
        
        if((float(data['Bomba de calor'].replace(',',".")) < 0.15) and (self.status==1) ):
            self.pushEvent({"datetime": data['Datetime'], "type":"Sistema", "msg": "El sistema se ha detenido"})
            self.status = 0

# Reconocer eventos a partir de las acciones del cliente sobre el DT
    def pushEventFromClient(self, my_event):

        # Arranque manual de la bomba
        if my_event["id"] == 0:
            curr_datetime = datetime.now()
            now = curr_datetime.strftime("%d-%m-%Y | %H:%M")
            self.pushEvent({"datetime": now, "type": my_event["tipo"], "msg": my_event["msg"]})
            return 1

        # Detención manual de la bomba
        if my_event["id"] == 1:
            curr_datetime = datetime.now()
            now = curr_datetime.strftime("%d-%m-%Y | %H:%M")
            self.pushEvent({"datetime":  now, "type": my_event["tipo"], "msg": my_event["msg"]})
            return 1

        # Cambio de la temperatura consignada
        if my_event["id"] == 2:
            curr_datetime = self.dba.getLastSensorValues()
            now = curr_datetime['Datetime']
            self.consigTemp = my_event["params"]
            self.pushEvent({"datetime":  now,
                            "type": my_event["tipo"],
                            "msg": my_event["msg"] + ": " + str(my_event["params"] + "C")
                            })
            return 1

        # Solicitud de arranque predictivo
        if my_event["id"] == 3:
            values = self.dba.getLastSensorValues()
            curr_datetime = values['Datetime']
            self.pushEvent({"datetime":  curr_datetime, "type": my_event["tipo"], "msg": "Sol. arranque intel." +": " + my_event["params"]})
            return 1
        
        else:
            return 0