import os
import json
import csv

def leer_archivos(directorio):
    pacientes = []

    for archivo in os.listdir(directorio):
        ruta = os.path.join(directorio, archivo)

        try:
            if archivo.endswith('.json'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    for d in datos:
                        d['ID'] = d.get('id')
                        pacientes.append({'archivo': archivo, 'datos': d})  

            elif archivo.endswith('.csv'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        row['ID'] = row.get('id')
                        pacientes.append({'archivo': archivo, 'datos': row})  

            elif archivo.endswith('.txt'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    lineas = [linea.strip() for linea in f.readlines()]
                    paciente = {
                        'DatosCrudos': lineas
                    }
                    pacientes.append({'archivo': archivo, 'datos': paciente}) 

        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

    return pacientes
