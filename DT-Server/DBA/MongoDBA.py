from pymongo import MongoClient, DESCENDING

class MongoDBA:
    def __init__(self):

        # Inicialización de la conexión
        self.host = 'localhost'
        self.port = 27017
        self.con = MongoClient(self.host, self.port)
        self.db = self.con.sensorDB
        self.col = self.db.rawdataCOL

# Obtener últimos registros de actividad de sensores almacenados en BBDD
    def getLastSensorValues(self):
        output = self.col.find_one(sort=[( '_id', DESCENDING )])
        if output:
            res = output
            print(res)
            res['_id'] = str(res['_id'])
            return res
        else:
            return None

# Añadir nuevo registro de actividad de los sensores a BBDD
    def postSensorValues(self, data):
        self.col.insert_one(data)
        print("Valores insersados en DB")

# Obtener dataset de registros de actividad solicitado para generar el modelo de tiempo de arranque
    def getDataset(self):
        dataset = self.col.find({},{
            '_id': 0,
            'Datetime': 1,
            'Bomba de calor': 1,
            'Temperatura aigua impuls': 1,
            'Temperatura consigna': 1,
            'Temperatura exterior (AEMET)' : 1,
        })
        if dataset:
            return dataset
        else:
            return None