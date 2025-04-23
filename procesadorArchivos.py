import os
import json
import csv

def leer_archivos(directorio):
    pacientes = []

    for archivo in os.listdir(directorio):
        ruta = os.path.join(directorio, archivo)

        try:
            
            if archivo.endswith('.txt'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    lineas = [linea.strip() for linea in f.readlines()]

                    paciente = {}
                    for linea in lineas:
                        # Línea con info del paciente (ID, Nombres, Apellidos,Genero y Edad)
                        if linea.startswith('3O|'):
                            partes = linea.split('|')
                            if len(partes) > 13:
                                paciente['ID'] = partes[2].strip()
                                paciente['Nombres'] = partes[12].strip()
                                paciente['Apellidos'] = partes[13].strip()
                                paciente['Genero'] = partes[27].strip()
                                if len(partes) > 4 and '^^^' in partes[4]:
                                    paciente['Edad'] = partes[4].replace('^^^', '').strip()

                        # Extraer solo los resultados de tipo AREA
                        if '|^^^' in linea and '^AREA' in linea:
                            partes = linea.split('|')
                            if len(partes) > 3:
                                campo = partes[2]
                                valor = partes[3]
                                try:
                                    _, _, _, nombre_prueba, metrica = campo.split('^')
                                    if metrica == 'AREA':
                                        paciente[nombre_prueba] = valor
                                except ValueError:
                                    continue  

                    pacientes.append({
                        'archivo': archivo,
                        'tipo_archivo': 'txt',
                        'datos': paciente
                    })
            elif archivo.endswith('.json'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    paciente = {}
                    for d in datos:
                        d['ID'] = d.get('id')
                        paciente['ID'] = d.get('id')
                        paciente['Nombres'] = d.get('Pname')
                        paciente['Apellidos'] = d.get('Plastname')
                        paciente['Genero'] = d.get('gender')
                        paciente['Edad'] = d.get('age')
                        test = d.get('test')
                        paciente['HDL'] = test['HDL']
                        paciente['LDL'] = test['LDL']
                        paciente['TRIG'] = test['TRIG']
                        #pacientes.append({'archivo': archivo, 'datos': d})  

                    pacientes.append({
                        'archivo': archivo,
                        'tipo_archivo': 'txt',
                        'datos': paciente
                    })
            
            elif archivo.endswith('.csv'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    reader.fieldnames = [campo.strip() for campo in reader.fieldnames]
                    paciente = {}
                    for row in reader:
                        paciente['ID'] = row.get('id')
                        print(row.get('id'))
                        paciente['Nombres'] = row.get('name')
                        paciente['Apellidos'] = row.get('lastname')
                        paciente['Genero'] = row.get('gender')
                        paciente['Edad'] = row.get('age')
                        paciente['TP'] = row.get('test_tp')
                        paciente['TPT'] = row.get('test_ptt')
                        paciente['FIB'] = row.get('test_fib')

                    pacientes.append({
                        'archivo': archivo,
                        'tipo_archivo': 'txt',
                        'datos': paciente
                    })
                        

                    '''

            
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
            '''  

        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

    return pacientes
