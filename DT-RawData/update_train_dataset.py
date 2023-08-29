import json
import datetime
import pandas as pd
import time

# SCRIPT DE TEST PARA CARGAR DATOS EN MONGODB ENTRE EL 23/03/2021 Y EL 26/03/2021
from pymongo import MongoClient
import requests

# CONSTANTS
#FILENAMES = ['temperatures.csv', 'circuit.csv', 'consum.csv']
FILENAMES = ['train_prediccio/temperatures.csv', 'train_prediccio/circuit.csv', 'train_prediccio/consum.csv']
FREQ = 45  # Tiempo entre cargas de nuevos valores
REAL_FREQ = 15  # Tiempo real entre tomas de datos de los sensores (horas)


############## METHODS ##############

# Inserta un nuevo valor en la colección --- AÑADIR CIFRADO???
def publish_values(list):
    col.insert_many(list)
    print("Values sent successfully")

def modify_temp_col(ds):

    # Modifica los valores de la columna 'Time' para las series ['Temperatura PB', 'Temperatura P1] ya que se dan en
    # momentos del tipo 12:25 o 12:55 (prev) --> 12:30 y 13:00 (post)

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

# NoSQL Database - Consultas puerto 27017
# server.local_bind_port is assigned local port

#cli = con = MongoClient('192.168.1.65', 27017)
host = 'localhost'
port = 27017
con = MongoClient(host, port)
db = con.sensorDB
col = db.rawdataCOL

dicts_list = []

# Inicializar y cargar dataset desde archivos csv
dataset_1 = pd.read_csv(FILENAMES[0], header=0, delimiter=';')
dataset_2 = pd.read_csv(FILENAMES[1], header=0, delimiter=';')
dataset_3 = pd.read_csv(FILENAMES[2], header=0, delimiter=';')

# Parche BUG --> *La hora de temperaturas interior ext no coinciden temporalmente*
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
last_time = '2021-03-25T22:00:00+0100'
last_time_obj = datetime.datetime.strptime(
    last_time, '%Y-%m-%dT%H:%M:%S%z')
idx = 0
total = 0

# Parche ERROR-5.2 --> *Temperatura exterior e interior aparece como NaN entre horas*  (Ej: 09:15, 09:45)
last_pb_value = 0
last_p1_value = 0
last_aemet_value = 0

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

            # Parche ERROR-5.2 --> *Temperatura exterior e interior aparece como NaN entre horas*  (Ej: 09:15, 09:45)
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

    row = dict(zip(headers, rd_row))

    print(row)

    rd_row = []

    # Insertar nuevo elemento en la colección
    #publish_values(row)
    dicts_list.append(row)

    # Esperar 15s -2h reales
    current_time_obj = current_time_obj + datetime.timedelta(minutes=REAL_FREQ)

    total = total + 1

publish_values(dicts_list)
print("Dataset was uploaded successfully")
