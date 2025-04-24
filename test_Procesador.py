from procesadorArchivos import leer_archivos
from hl7_generator import generar_hl7_txt
import json
import os

def test_lectura():
    carpeta_entrada = 'data'
    carpeta_salida = 'salida'

    pacientes = leer_archivos(carpeta_entrada)

    print("Se cargaron", len(pacientes), "pacientes")
    for p in pacientes:
        archivo = p.get('archivo', 'Desconocido')
        print(f"{archivo} -> ")
        print(json.dumps(p['datos'], ensure_ascii=False, indent=4))

        # Generar archivo HL7 por paciente
        generar_hl7_txt(p, carpeta_salida)

if __name__ == "__main__":
    test_lectura()
