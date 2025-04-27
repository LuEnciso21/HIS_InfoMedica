import os

def generar_hl7_txt(paciente, salida_dir):
    """
    Genera HL7 (.hl7.txt) con MSH, PID, OBR y OBX.
    """
    if not os.path.exists(salida_dir):
        os.makedirs(salida_dir)

    full = paciente.get('datos_completos', {})
    dat = paciente['datos']

    # Nombre base del archivo sin la extensión múltiple
    nombre_base = paciente['archivo'].replace('.', '_') + '.hl7'
    versiones_existentes = [
        f for f in os.listdir(salida_dir)
        if f.startswith(nombre_base) and f.endswith('.txt')
    ]

    if not versiones_existentes:
        fname = f"{nombre_base}.txt"
    else:
        nueva_version = len(versiones_existentes)
        fname = f"{nombre_base}.{nueva_version}.txt"

    path = os.path.join(salida_dir, fname)

    # MSH Segment
    msh = [
        'MSH', '^~\\&', full.get('device', ''), full.get('ips', ''),
        full.get('model', ''), full.get('serial', ''), full.get('date', ''),
        '', 'ORU^R01', full.get('control_id', ''), 'P', '2.5.1'
    ]
    lines = ['|'.join(msh)]

    # PID Segment (use updated names if available)
    pid = [
        'PID', '', '', str(dat.get('ID', '')), '',
        f"{dat.get('Apellidos', '')}^{dat.get('Nombres', '')}", '',str(dat.get('Edad', '')),
        dat.get('Genero', ''), '', '', 
    ]
    lines.append('|'.join(pid))

    # OBR Segment
    obr = [
        'OBR', '1', '', '', '', '', '', '', '', '', '', '', '',
        f"{full.get('physician','')}^{full.get('specialty','')}", '', full.get('admission','')
    ]
    lines.append('|'.join(obr))

    # OBX Segment
    skip = {
        'id','Pname','name','lastname','Plastname','gender','age','date','header_info',
        'device','ips','model','serial','control_id','physician','admission','specialty',
        'Nombres','Apellidos','Genero','ID','Edad','dx2','dx3','dx4','dx5'
    }
    for k, v in full.items():
        if k in skip:
            continue
        if isinstance(v, dict):
            for sk, sv in v.items():
                lines.append(f"OBX|||{sk}||{sv}||||||F")
        elif isinstance(v, list):
            for it in v:
                lines.append(f"OBX|||{k}||{it}||||||F")
        else:
            lines.append(f"OBX|||{k}||{v}||||||F")

    with open(path, 'w', encoding='utf-8') as f:
        f.write("\r\n".join(lines))


def actualizar_hl7_txt(paciente, salida_dir,msh,obr,obx):
    """
    Genera HL7 (.hl7.txt) con MSH, PID, OBR y OBX.
    """
    if not os.path.exists(salida_dir):
        os.makedirs(salida_dir)

    full = paciente.get('datos_completos', {})
    dat = paciente['datos']

    # Nombre base del archivo sin la extensión múltiple
    nombre_base = paciente['archivo'].replace('.', '_') + '.hl7'
    versiones_existentes = [
        f for f in os.listdir(salida_dir)
        if f.startswith(nombre_base) and f.endswith('.txt')
    ]

    if not versiones_existentes:
        fname = f"{nombre_base}.txt"
    else:
        nueva_version = len(versiones_existentes)
        fname = f"{nombre_base}.{nueva_version}.txt"

    path = os.path.join(salida_dir, fname)

    # MSH Segment
    lines = []
    lines.append(msh)

    # PID Segment (use updated names if available)
    pid = [
        'PID', '', '', str(dat.get('ID', '')), '',
        f"{dat.get('Apellidos', '')}^{dat.get('Nombres', '')}", '',str(dat.get('Edad', '')),
        dat.get('Genero', ''), '', '', 
    ]
    lines.append('|'.join(pid))

    # OBR Segment
    lines.append(obr)

    for obx_line in obx:
        lines.append(obx_line)

    # OBX Segment
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\r\n".join(lines)) 