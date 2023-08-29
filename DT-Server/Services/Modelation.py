import time
import threading
import pickle
from pandas import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

class Modelation:
    def __init__(self, dba, constants):
        self.dba = dba

        self.bootTimeModel = None
        self.bootTimeModelUpdateFreq = 45
        self.filename = 'Models/model.pkl'

    # Generación y actualización del modelo de tiempo de arranque en segundo plano
        t = threading.Thread(target=self.startBootTimeModel)
        t.start()

# Actualizar modelo de tiempo de arranque
    def updateBootTimeModel(self):

        #Se cargan los valores de input
        d0 = self.dba.getDataset()
        d1 = []

        # Solo interesa la actividad registrada mientras la bomba logra alcanzar la temperatura deseada
        for item in d0:
            if (float(item['Bomba de calor'].replace(',',".")) > 0.15) and (len(item) == 5):
                d1.append(self.formatDataToString(item))

        #Formato de dataframe que permitirá generar el modelo
        # input --> 'Temperatura aigua impuls', 'Temperatura consigna', 'Temperatura exterior (AEMET)', 'Temperatura exterior (esperada)'
        # output --> 'Tiempo arranque'
        headers = ['Temperatura aigua impuls', 'Temperatura consigna', 'Temperatura exterior (AEMET)', 'Temperatura exterior (esperada)', 'Tiempo arranque']

        # Conversión del dataset incial al formato de dataset solicitado
        dataset = []
        for curr_item in d1:
            curr_item_time = curr_item['Datetime']
            curr_item_time_obj = datetime.strptime(curr_item_time, '%Y-%m-%dT%H:%M:%S%z')

            reg_set  = 0
            for aux_item in d1:
                aux_item_time_obj = datetime.strptime(aux_item['Datetime'], '%Y-%m-%dT%H:%M:%S%z')
                pred_time_min = self.datetimeDiffInMinutes(curr_item_time_obj, aux_item_time_obj)

                if (curr_item_time_obj <= aux_item_time_obj) and (int(aux_item['Temperatura aigua impuls']) >= 55) and (pred_time_min<=500):
                    # data = {'Temperatura aigua impuls (x1), Temperatura consigna (x2), Temperatura exterior (x3), Tiempo arranque (y1)
                    #Hay que convertir a float los valores
                    temp_impuls = (float(curr_item['Temperatura aigua impuls'].replace(',',".")))
                    temp_consigna = (float(curr_item['Temperatura consigna'].replace(',',".")))
                    temp_exterior = (float(curr_item['Temperatura exterior (AEMET)'].replace(',',".")))
                    temp_exterior_pred = (float(aux_item['Temperatura exterior (AEMET)'].replace(',',".")))

                    data = [temp_impuls, temp_consigna, temp_exterior, temp_exterior_pred, float(pred_time_min)]

                    dataset.append(dict(zip(headers, data)))
                    reg_set = 1

                if reg_set == 1:
                    break
                else:
                    continue

        # Separación de columnas en input/output
        df = pd.DataFrame.from_dict(dataset)
        x = df.iloc[:, 0:-1] #Las columnas tempConsignada, tempActual, tempPredecida son los inputs
        y = df.iloc[:, -1] #La columna TArranque es el output

        # Creación del modelo
        model = LinearRegression()
        model.fit(x, y)

        #Se guarda el modelo en los archivos del servidor
        file = open('model.pkl','wb')
        pickle.dump(model, file)

        return 1

# Método principal de generación del modelo, se actualiza cada X tiempo
    def startBootTimeModel(self):
        while True:
            res = self.updateBootTimeModel()
            if res:
                print("Se ha actualizado el modelo")
            #Recarga del modelo cada X segundos
            time.sleep(self.bootTimeModelUpdateFreq)

# Parse de valores de dict a formato string
    def formatDataToString(self, data):
        for value in data:
            if(isinstance(data[value], str)==False):
                data[value]=str(data[value])
        return data

# Diferencia de tiempo en objetos datetime en minutos
    def datetimeDiffInMinutes(self, curr_time_obj, sch_time_obj):
        diff = sch_time_obj - curr_time_obj
        diff_seconds = diff.total_seconds()  # Diferencia de horas en segundos
        return divmod(diff_seconds, 60)[0]  # Diferencia de horas en horas
