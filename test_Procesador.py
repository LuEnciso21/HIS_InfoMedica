from procesadorArchivos import leer_archivos
import json

def test_lectura():
    pacientes = leer_archivos('data')

    print("Se cargaron", len(pacientes), "pacientes:")
    for p in pacientes:
        archivo = p.get('archivo', 'Desconocido')  # Obtener el nombre del archivo
        
        # Imprimir el nombre del archivo primero
        print(f"{archivo} -> ")
        
        # Imprimir los datos del paciente
        print(json.dumps(p['datos'], indent=4))  

if __name__ == "__main__":
    test_lectura()


