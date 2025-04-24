import os
import json
import csv

def leer_archivos(directorio):
    """
    Recorre archivos .txt, .json y .csv dentro de `directorio`, extrae datos del paciente.
    Devuelve una lista de diccionarios con:
      - archivo: nombre del archivo original
      - tipo_archivo: 'txt', 'json' o 'csv'
      - datos: diccionario reducido (para base de datos)
      - datos_completos: objeto completo (para generar HL7)
    """
    pacientes = []

    for archivo in os.listdir(directorio):
        ruta = os.path.join(directorio, archivo)
        try:
            if archivo.endswith('.txt'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    lineas = [l.strip() for l in f]
                paciente = {}
                for linea in lineas:
                    if linea.startswith('1H|'):
                        partes_h = linea.split('|')
                        if len(partes_h) > 1:
                            paciente['date'] = partes_h[-1]
                        if len(partes_h) > 4:
                            paciente['header_info'] = partes_h[3]
                    if linea.startswith('3O|'):
                        partes = linea.split('|')
                        if len(partes) > 13:
                            paciente['ID'] = partes[2].strip()
                            paciente['Nombres'] = partes[12].strip()
                            paciente['Apellidos'] = partes[13].strip()
                            paciente['Genero'] = partes[27].strip()
                            if '^^^' in partes[4]:
                                paciente['Edad'] = partes[4].replace('^^^','').strip()
                    if '|^^^' in linea and '^AREA' in linea:
                        partes = linea.split('|')
                        if len(partes) > 3:
                            campo, valor = partes[2], partes[3]
                            try:
                                _,_,_,nombre_prueba,metrica = campo.split('^')
                                if metrica=='AREA':
                                    paciente[nombre_prueba] = valor
                            except ValueError:
                                pass
                pacientes.append({'archivo':archivo,'tipo_archivo':'txt','datos':paciente,'datos_completos':paciente})

            elif archivo.endswith('.json'):
                with open(ruta,'r',encoding='utf-8') as f:
                    datos = json.load(f)
                for d in datos:
                    pac = {
                        'ID': d.get('id'),
                        'Nombres': d.get('Pname'),
                        'Apellidos': d.get('Plastname'),
                        'Genero': d.get('gender'),
                        'Edad': d.get('age'),
                        'HDL': d.get('test',{}).get('HDL'),
                        'LDL': d.get('test',{}).get('LDL'),
                        'TRIG': d.get('test',{}).get('TRIG')
                    }
                    pacientes.append({'archivo':archivo,'tipo_archivo':'json','datos':pac,'datos_completos':d})

            elif archivo.endswith('.csv'):
                with open(ruta,'r',encoding='utf-8') as f:
                    reader = csv.DictReader(f,delimiter=';')
                    reader.fieldnames = [c.strip() for c in reader.fieldnames]
                    for row in reader:
                        pac = {k: row.get(k,'').strip() for k in ['id','name','lastname','gender','age','test_tp','test_ptt','test_fib']}
                        pacientes.append({'archivo':archivo,'tipo_archivo':'csv','datos':{
                            'ID':pac['id'],'Nombres':pac['name'],'Apellidos':pac['lastname'], 'Genero':pac['gender'],'Edad':pac['age'],
                            'TP':pac['test_tp'],'TPT':pac['test_ptt'],'FIB':pac['test_fib']
                        },'datos_completos':row})
        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")
    return pacientes
