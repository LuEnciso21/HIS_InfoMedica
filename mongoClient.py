from pymongo import MongoClient

# URI real de conexión
client = MongoClient("mongodb+srv://luisaenciso:x1Mi0hf2Mkfx52c7@cluster0.k81bolw.mongodb.net/his_db?retryWrites=true&w=majority&tls=true")

# Base de datos y colección
db = client['his_db']
coleccion = db['pacientes']

# Verificar la conexión
try:
    client.admin.command('ping')
    print("✅ Conexión exitosa a MongoDB")
except Exception as e:
    print(f"❌ Error de conexión a MongoDB: {e}")

def insertar(pacientes):
    try:
        if isinstance(pacientes, list):
            result = coleccion.insert_many(pacientes)
            print(f"Datos insertados exitosamente. IDs de documentos insertados: {result.inserted_ids}")
        else:
            result = coleccion.insert_one(pacientes)
            print(f"Dato insertado exitosamente. ID de documento insertado: {result.inserted_id}")
    except Exception as e:
        print(f"Error al insertar los datos en MongoDB: {e}")

def buscar(id):
    return coleccion.find_one({"ID": id})

def actualizar(id, nuevos_datos):
    return coleccion.update_one({"ID": id}, {"$set": nuevos_datos})

def eliminar(id):
    return coleccion.delete_one({"ID": id})
