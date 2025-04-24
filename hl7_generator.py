import os

def generar_hl7_txt(paciente, salida_dir):
    """
    Genera HL7 (.hl7.txt) con MSH, PID, OBR y OBX.
    """
    if not os.path.exists(salida_dir): os.makedirs(salida_dir)
    full = paciente.get('datos_completos',{})
    dat  = paciente['datos']
    fname = paciente['archivo'].replace('.','_')+'.hl7.txt'
    path  = os.path.join(salida_dir,fname)
    
    msh=[
        'MSH','^~\\&',full.get('device',''),full.get('ips',''),
        full.get('model',''),full.get('serial',''),full.get('date',''),
        '','ORU^R01',full.get('control_id',''), 'P','2.5.1'
    ]
    lines=['|'.join(msh)]
    
    pid=['PID','','',str(dat.get('ID','')),'',f"{dat.get('Apellidos','')}^{dat.get('Nombres','')}" ,'','',dat.get('Genero',''),'','',str(dat.get('Edad',''))]
    lines.append('|'.join(pid))
    
    obr=[
        'OBR','1','','',
        f"^{full.get('header_info','')}^", '', full.get('date',''),
        '', '', '', '', '', '',
        full.get('physician',''), '', full.get('admission','')
    ]
    lines.append('|'.join(obr))
    
    skip={'id','Pname','name','lastname','Plastname','gender','age','date','header_info','device','ips','model','serial','control_id','physician','admission','Nombres','Apellidos','Genero','ID','Edad'}
    for k,v in full.items():
        if k in skip: continue
        if isinstance(v,dict):
            for sk,sv in v.items(): lines.append(f"OBX|||{sk}||{sv}||||||F")
        elif isinstance(v,list):
            for it in v: lines.append(f"OBX|||{k}||{it}||||||F")
        else: lines.append(f"OBX|||{k}||{v}||||||F")

    with open(path,'w',encoding='utf-8') as f: f.write("\r\n".join(lines))
