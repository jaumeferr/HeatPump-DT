import json
import datetime
import pandas as pd
import time
from MQTTClient import MQTTClient

# CONSTANTES
#FILENAMES = ['alerts_test/temperatures.csv', 'alerts_test/circuit.csv', 'alerts_test/consum.csv'] # --- Histórico completo de datos
FILENAMES = ['test_prediccio/temperatures.csv', 'test_prediccio/circuit.csv', 'test_prediccio/consum.csv'] # -- Registros simulados
FREQ = 15  # Tiempo entre cargas de nuevos valores
REAL_FREQ = 15  # Tiempo real entre tomas de datos de los sensores (min)


############## MÉTODOS ##############

# Inserta un nuevo valor en la colección
def publish_values(row):
    mqtt.updateValues(json.dumps(row))
    print("Values sent successfully")

# Modifica los valores de la columna 'Time' para las series ['Temperatura PB', 'Temperatura P1] ya que se dan en
    # momentos del tipo 12:25 o 12:55 (antes) --> 12:30 y 13:00 (después)
def modify_temp_col(ds):
    for index, row in ds.iterrows():

        c_time = row['Time']

        if row['Series'] == 'Temperatura PB' or row['Series'] == 'Temperatura P1':
            # Sumar 5 minutos ------

            # String to date object
            time_obj = datetime.datetime.strptime(
                c_time, '%Y-%m-%dT%H:%M:%S%z')

            # Date object + 5 min
            time_obj = time_obj + datetime.timedelta(minutes=5)

            # Date object to String
            c_time = time_obj.strftime('%Y-%m-%dT%H:%M:%S%z')[:-2] + ':' + time_obj.strftime('%Y-%m-%dT%H:%M:%S%z')[-2:]

        ds.at[index, 'Time'] = c_time

    return ds


##############  MAIN  ##############

# Abrir conexión MQTT con el broker
mqtt_broker = "192.168.1.64"
mqtt_port = 1883
mqtt_client_id = "mosquitto_client_01"
mqtt = MQTTClient(mqtt_broker, mqtt_port)
mqtt.openMQTT()

# Inicializar y cargar dataset desde archivos csv
dataset_1 = pd.read_csv(FILENAMES[0], header=0, delimiter=';')
dataset_2 = pd.read_csv(FILENAMES[1], header=0, delimiter=';')
dataset_3 = pd.read_csv(FILENAMES[2], header=0, delimiter=';')

# Parche ERROR --> *La hora de temperaturas interior ext no coinciden temporalmente*
dataset_1 = modify_temp_col(dataset_1)

# Concatenar dataset y agrupar por fecha
dataset = pd.concat([dataset_1, dataset_2, dataset_3])
dataset.sort_values(by=['Time', 'Series'], inplace=True)
dataset = dataset.reset_index(drop=True)

# Tipos de dato
series = dataset.Series.unique()
series = series.tolist()
headers = ['Datetime'] + series

# Control de tiempo
current_time = dataset.at[0, 'Time']
current_time_obj = datetime.datetime.strptime(
    current_time, '%Y-%m-%dT%H:%M:%S%z')

# Control fin de fichero
last_time = dataset.at[dataset.__len__()-1, 'Time']
last_time_obj = datetime.datetime.strptime(
    last_time, '%Y-%m-%dT%H:%M:%S%z')
idx = 0
total = 0

# Parche ERROR --> *Temperatura exterior e interior aparece como NaN entre horas*  (Ej: 09:15, 09:45)
last_pb_value = 0
last_p1_value = 0
last_aemet_value = 0

# Se envían períodicamente los registros del dataset principal (dataset).
# Conversión a realizar:
# 
# ej:temperatures.csv      -------->        dataset final:

# serie          valor   date               datetime    valor_serie_1   valor_serie_2   valor_serie_3
#
# nombre_serie_1 valor_1 datetime_1            date_1    valor_1         valor_1         valor_1
# nombre_serie_2 valor_1 datetime_1            date_2    valor_2         valor_2         valor_2
# nombre_serie_3 valor_1 datetime_1            ...
# nombre_serie_1 valor_1 datetime_2
# nombre_serie_2 valor_2 datetime_2
# nombre_serie_3 valor_2 datetime_2
# ...

while current_time_obj < last_time_obj:
    rd_row = []
    current_data = dataset.loc[dataset['Time'] == current_time_obj.strftime(
        '%Y-%m-%dT%H:%M:%S%z')[:-2] + ':' + current_time_obj.strftime('%Y-%m-%dT%H:%M:%S%z')[-2:]]

    rd_row.append(current_time_obj.strftime('%Y-%m-%dT%H:%M:%S%z'))

    # Obtener Value según el tipo de Series para la fecha actual (Tener en cuenta valores NaN)
    for i in series:
        sel_row = current_data.loc[current_data['Series'] == i]

        if sel_row.empty == False:
            # array([['Temperatura P1', '2020-12-05T19:00:00+01:00', '16.75']], dtype=object) --> value found at row.values[0,2]
            value = sel_row.values[0, 2]

            rd_row.append(value)


            # Parche ERROR --> *Temperatura exterior e interior aparece como NaN entre horas*  (Ej: 09:15, 09:45)
            if i == 'Temperatura PB':
                last_pb_value = value

            if i == 'Temperatura P1':
                last_p1_value = value

            if i == 'Temperatura exterior (AEMET)':
                last_aemet_value = value

        else:
            # Parche ERROR-5.2 --> *Temperatura exterior e interior aparece como NaN entre horas*  (Ej: 09:15, 09:45)
            if i == 'Temperatura PB':
                rd_row.append(last_pb_value)

            if i == 'Temperatura P1':
                rd_row.append(last_p1_value)

            if i == 'Temperatura exterior (AEMET)':
                rd_row.append(last_aemet_value)

    #Crear nuevo dict a partir según los nombres de series (columnas)
    row = dict(zip(headers, rd_row))

    rd_row = []

    # Insertar nuevo elemento en la colección
    publish_values(row)

    # Sleep de 15s - 15 min en el entorno real
    current_time_obj = current_time_obj + datetime.timedelta(minutes=REAL_FREQ)
    time.sleep(FREQ)

    total = total + 1

print("Dataset was uploaded successfully")
print("Items:  " + total)
