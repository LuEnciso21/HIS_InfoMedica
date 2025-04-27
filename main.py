from nicegui import ui
import os
from procesadorArchivos import leer_archivos
from hl7_generator import generar_hl7_txt, actualizar_hl7_txt
from mongoClient import insertar, buscar, actualizar, eliminar

# --- Etiqueta principal para mensajes globales ---
data_label = ui.label("").classes('mt-4 text-center')

# --- Página principal ---
@ui.page("/")
def main_page():
    # Encabezado
    with ui.row().classes('w-full bg-[#4d82bc] text-white p-4 items-center justify-between'):
        ui.image("LOGOHOSPITAL_R.png").classes('w-16 h-auto')
        ui.label("SISTEMA DE INFORMACIÓN HOSPITALARIA").classes('text-3xl font-bold flex-1 text-center')
        ui.label().classes('w-16')  # placeholder

    # Botones de acción
    with ui.row().classes('gap-3 my-6 justify-center'):
        ui.button("📂 Cargar datos desde archivos", on_click=cargar_datos).classes('px-6 py-2 rounded-lg shadow')
        ui.button("🔍 Buscar paciente", on_click=abrir_busqueda).classes('px-6 py-2 rounded-lg shadow')
        ui.button("📝 Actualizar paciente", on_click=abrir_actualizacion).classes('px-6 py-2 rounded-lg shadow')
        ui.button("🗑️ Eliminar paciente", on_click=abrir_eliminacion).classes('px-6 py-2 rounded-lg shadow')

    # Carrusel de imágenes
    with ui.carousel(animated=True, arrows=True, navigation=True).props('autoplay').classes('w-full h-64 mb-6'):
        for img in ['98.webp', '87.jpg', '100.jpg']:
            with ui.carousel_slide().classes('p-0'):
                ui.image(img).classes('w-full h-full object-cover')

    # Mensaje de estado
    ui.label().bind_text_from(data_label, 'value').classes('text-lg')

# --- Función para cargar archivos y agregar pacientes ---
def cargar_datos():
    datos = leer_archivos('data')
    nuevos = 0
    ruta = 'salida'
    os.makedirs(ruta, exist_ok=True)

    for paciente in datos:
        pd = paciente['datos']
        if all(k in pd for k in ('ID', 'Nombres', 'Apellidos')) and not buscar(pd['ID']):
            insertar(pd)
            generar_hl7_txt(paciente, ruta)
            nuevos += 1

    mensaje = (f"✅ {nuevos} pacientes insertados y HL7 generados." if nuevos else "⚠️ No hay pacientes nuevos.")
    ui.notify(mensaje, duration=4000)
    data_label.value = mensaje

# --- Función para buscar paciente ---
def abrir_busqueda():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-80'):
        ui.label("🔍 Buscar paciente").classes('text-xl font-semibold mb-3')
        id_input = ui.input("ID del paciente").classes('mb-3')
        result_label = ui.label().classes('text-sm text-red-600 mb-3')

        def b():
            p = buscar(id_input.value)
            if p:
                ocultos = {'_id', 'header_info', 'device', 'ips', 'model', 'serial', 'date', 'control_id'}
                display = {k: v for k, v in p.items() if k not in ocultos}
                txt = "\n".join(f"• {k}: {v}" for k, v in display.items())
                with ui.dialog() as d2, ui.card().classes('p-4 w-80'):
                    ui.label("👤 Datos del paciente").classes('text-lg font-medium mb-2')
                    ui.label(txt).classes('whitespace-pre-wrap mb-4')
                    ui.button("Cerrar", on_click=d2.close).classes('px-4')
                d2.open()
            else:
                result_label.text = "⚠️ Paciente no encontrado"

        ui.button("Buscar", on_click=b).classes('mr-2 px-4')
        ui.button("Cerrar", on_click=dialog.close).classes('px-4')
    dialog.open()

# --- Función para actualizar paciente ---
def abrir_actualizacion():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-80'):
        ui.label("📝 Actualizar paciente").classes('text-xl font-semibold mb-3')
        id_input = ui.input("ID del paciente").classes('mb-3')
        info = ui.label().classes('whitespace-pre-wrap text-sm mb-2')
        aviso = ui.label().classes('text-sm text-gray-500 mb-2')
        nuevos_input = ui.input("Datos (ej: Edad:35,device:XYZ)").classes('mb-3')
        nuevos_input.visible = False
        result = ui.label().classes('text-sm text-red-600 mb-3')

        archivo_original = {'msh': None, 'obr': None, 'obx': None, 'file': None}

        def buscar_archivo(idn):
            ruta = 'salida'
            if not os.path.exists(ruta): return None
            for f in os.listdir(ruta):
                if f.endswith('.txt'):
                    with open(os.path.join(ruta, f), 'r', encoding='utf-8') as h:
                        msh = obr = None; obx = []
                        for line in h:
                            if line.startswith('MSH'): msh = line.strip()
                            if line.startswith('PID') and int(line.split('|')[3]) == idn:
                                for L in h:
                                    if L.startswith('OBR'): obr = L.strip()
                                    elif L.startswith('OBX'): obx.append(L.strip())
                                break
                        if msh and obr: return msh, obr, obx, f
            return None

        def load():
            p = buscar(id_input.value)
            if not p:
                info.text = "⚠️ Paciente no encontrado"
                return
            res = buscar_archivo(int(id_input.value))
            if not res:
                info.text = "⚠️ Archivo HL7 no encontrado"
                return
            msh, obr, obx, fn = res
            archivo_original.update({'msh': msh, 'obr': obr, 'obx': obx, 'file': fn})
            ocultos = {'_id', 'header_info', 'device', 'ips', 'model', 'serial', 'date', 'control_id'}
            display = {k: v for k, v in p.items() if k not in ocultos}
            info.text = "\n".join(f"• {k}: {v}" for k, v in display.items())
            aviso.text = "Ingrese campos a actualizar"
            nuevos_input.visible = True
            load_btn.delete()
            ui.button("Actualizar", on_click=update).classes('px-4')

        def update():
            try:
                raw = dict(pair.split(":", 1) for pair in nuevos_input.value.split(","))
            except:
                result.text = "⚠️ Formato inválido"; return
            raw.pop('ID', None)
            if not raw:
                result.text = "⚠️ Sin datos para actualizar"; return
            p = buscar(id_input.value)
            campos_msh = {'device','ips','model','serial','date','control_id'}
            campos_db = set(k for k in p.keys() if k not in campos_msh and k != '_id')
            valid = campos_db.union(campos_msh)
            nuevos = {k: v for k, v in raw.items() if k in valid}
            if not nuevos:
                result.text = "⚠️ Ningún campo válido"; return
            actualizar(id_input.value, nuevos)
            parts = archivo_original['msh'].split('|')
            pos = {'device':2,'ips':3,'model':4,'serial':5,'date':6,'control_id':9}
            for k, i in pos.items():
                if k in nuevos: parts[i] = nuevos[k]
            new_msh = '|'.join(parts)
            full = {'archivo': os.path.splitext(archivo_original['file'])[0] + '_upd', 'datos': buscar(id_input.value), 'datos_completos': buscar(id_input.value)}
            actualizar_hl7_txt(full, 'salida', new_msh, archivo_original['obr'], archivo_original['obx'])
            ui.notify("✅ Actualización completa", duration=3000)
            dialog.close()

        load_btn = ui.button("Cargar datos", on_click=load).classes('px-4 mb-2')
        ui.button("Cerrar", on_click=dialog.close).classes('px-4')
    dialog.open()

# --- Función para eliminar paciente ---
def abrir_eliminacion():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-72'):
        ui.label("🗑️ Eliminar paciente").classes('text-xl font-semibold mb-3')
        id_input = ui.input("ID del paciente").classes('mb-3')

        def do():
            r = eliminar(id_input.value)
            msg = "✅ Paciente eliminado" if r.deleted_count else "⚠️ Paciente no encontrado"
            ui.notify(msg, duration=3000)
            dialog.close()

        ui.button("Eliminar", on_click=do).classes('px-4 mr-2')
        ui.button("Cerrar", on_click=dialog.close).classes('px-4')
    dialog.open()

# --- Iniciar servidor ---
if __name__ in {"__main__","__mp_main__"}:
    ui.run()
