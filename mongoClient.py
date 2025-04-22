from pymongo import MongoClient

# URI real de conexión
#client = MongoClient("mongodb+srv://luisaenciso:x1Mi0hf2Mkfx52c7@cluster0.k81bolw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient("mongodb+srv://luisaenciso:x1Mi0hf2Mkfx52c7@cluster0.k81bolw.mongodb.net/his_db?retryWrites=true&w=majority&tls=true")

# Base de datos y colección
db = client['his_db']
coleccion = db['pacientes']

def insertar(pacientes):
    if isinstance(pacientes, list):
        coleccion.insert_many(pacientes)
    else:
        coleccion.insert_one(pacientes)

def buscar(id):
    return coleccion.find_one({"ID": id})

def actualizar(id, nuevos_datos):
    return coleccion.update_one({"ID": id}, {"$set": nuevos_datos})

def eliminar(id):
    return coleccion.delete_one({"ID": id})
