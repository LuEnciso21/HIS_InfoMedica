from nicegui import ui
import os
from procesadorArchivos import leer_archivos
from hl7_generator import generar_hl7_txt, actualizar_hl7_txt
from mongoClient import insertar, buscar, actualizar, eliminar

# --- Etiqueta principal para mensajes globales ---
data_label = ui.label("").style("margin-top: 20px;")

# --- Página principal ---
@ui.page("/")
def main_page():
    # --- Encabezado tipo barra superior con título centrado y nombre del hospital a la derecha ---
    with ui.row().classes('w-full bg-[#4d82bc] text-white p-2 items-center justify-between'):  # Cambié el color de fondo
        ui.label().classes('w-[110px]')
        
        # Texto central
        ui.label("SISTEMA DE INFORMACIÓN HOSPITALARIA").classes('text-2xl font-semibold text-center flex-1')
        
        # Mostrar la imagen del hospital
        ui.image("LOGOHOSPITAL_R.png").classes('w-[110px] h-auto text-right')

    with ui.row():
        ui.button("📂 Cargar datos desde archivos", on_click=cargar_datos)
        ui.button("🔍 Buscar paciente", on_click=abrir_busqueda)
        ui.button("📝 Actualizar paciente", on_click=abrir_actualizacion)
        ui.button("🗑️ Eliminar paciente", on_click=abrir_eliminacion)
    
    # --- Carrusel de imágenes debajo de los botones ---
    with ui.carousel(
        animated=True,
        arrows=True,
        navigation=True
    ).props('autoplay').classes('w-full h-[calc(100vh-160px)]'):
        with ui.carousel_slide().classes('p-0'):
            ui.image('98.webp').classes('w-full h-full object-cover')
        with ui.carousel_slide().classes('p-0'):
            ui.image('87.jpg').classes('w-full h-full object-cover')
        with ui.carousel_slide().classes('p-0'):
            ui.image('100.jpg').classes('w-full h-full object-cover')

    ui.label().bind_text_from(data_label, 'value')

# --- Función para cargar archivos y agregar pacientes ---

def cargar_datos():
    datos = leer_archivos('data')
    pacientes_a_insertar = []
    ruta = 'salida'

    # Crear la carpeta si no existe
    os.makedirs(ruta, exist_ok=True)

    for paciente in datos:
        paciente_data = paciente.get('datos', {})
        if 'ID' in paciente_data and 'Nombres' in paciente_data and 'Apellidos' in paciente_data:
            existente = buscar(paciente_data['ID'])
            if not existente:
                pacientes_a_insertar.append(paciente_data)
                generar_hl7_txt(paciente, ruta)  # ← Se genera HL7 para cada paciente nuevo

    if pacientes_a_insertar:
        insertar(pacientes_a_insertar)
        mensaje = f"📂 {len(pacientes_a_insertar)} pacientes nuevos insertados y archivos HL7 generados."
    else:
        mensaje = "⚠️ No hay pacientes nuevos para insertar."
    
    # Mostrar el mensaje en una notificación emergente
    ui.notify(mensaje, duration=5000)  # Duración en milisegundos (5 segundos)



# --- Función para buscar paciente ---
def abrir_busqueda():
    with ui.dialog() as dialog_busqueda, ui.card():
        ui.label("Buscar paciente por ID")
        id_input = ui.input("ID del paciente")
        result_label = ui.label()

        def buscar_paciente():
            paciente = buscar(id_input.value)
            if paciente:
                if '_id' in paciente:
                    paciente['_id'] = str(paciente['_id'])  # Evitar error de serialización

                texto = "\n".join(f"{k}: {v}" for k, v in paciente.items())

                with ui.dialog() as dialog_resultado, ui.card():
                    ui.label("👤 Datos del paciente").classes("text-lg font-bold")
                    ui.label(texto).classes("whitespace-pre-wrap")
                    ui.button("Cerrar", on_click=dialog_resultado.close)

                dialog_resultado.open()
            else:
                result_label.text = "⚠️ Paciente no encontrado"

        ui.button("Buscar", on_click=buscar_paciente)
        ui.button("Cerrar", on_click=dialog_busqueda.close)
        result_label

    dialog_busqueda.open()

# --- Función para actualizar paciente ---
def abrir_actualizacion():
    with ui.dialog() as dialog, ui.card():
        ui.label("Actualizar paciente")
        id_input = ui.input("ID del paciente")
        result_label = ui.label()
        info_paciente = ui.label().classes("whitespace-pre-wrap text-sm text-left")
        info1 = ui.label("Digitar el campo literal como se muestra en pantalla").classes("text-sm text-gray-600 mb-1")
        info2 = ui.label("Ej: Nombres:----,Apellidos:Cruz").classes("text-sm text-gray-600 mb-2")

        nuevos_input = ui.input("Datos(ej: Edad:35,Nombres:Pedro)")
        info1.visible = False
        info2.visible = False
        nuevos_input.visible = False
        archivo_original = {'nombre': None}

        def buscar_archivo_por_id(id_buscado):
            ruta_salida = 'salida'
            if not os.path.exists(ruta_salida):
                return None

            for archivo in os.listdir(ruta_salida):
                if archivo.endswith('.txt'):
                    ruta_archivo = os.path.join(ruta_salida, archivo)
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        obx_seg = []  # Inicializamos la lista para los segmentos OBX
                        for linea in f:
                            if linea.startswith('MSH'):
                                    msh = linea.strip()
                            if linea.startswith('PID'):
                                segmentos = linea.split('|')
                                if len(segmentos) >= 4 and int(segmentos[3]) == id_buscado:
                                    for linea in f:  # Continuamos leyendo después de PID
                                        if linea.startswith('MSH'):
                                            msh = linea.strip()
                                        elif linea.startswith('OBR'):
                                            obr = linea.strip()
                                        elif linea.startswith('OBX'):
                                            obx = linea.strip()
                                            obx_seg.append(obx)  # Agregar cada OBX encontrado
                                    return msh, obr, obx_seg, archivo  # Retornamos los segmentos y el archivo
            return None

        def cargar_y_mostrar():
            paciente = buscar(id_input.value)
            if paciente:
                msh,obr,obx,archivo_encontrado = buscar_archivo_por_id(int(id_input.value))
                if archivo_encontrado:
                    archivo_original['nombre'] = archivo_encontrado

                if '_id' in paciente:
                    paciente['_id'] = str(paciente['_id'])
                texto = "\n".join(f"{k}: {v}" for k, v in paciente.items())
                info_paciente.text = texto
                info1.visible = True
                info2.visible = True
                nuevos_input.visible = True
                cargar_button.delete()

                def actualizar_paciente():
                    try:
                        nuevos_datos_raw = dict(pair.split(":") for pair in nuevos_input.value.split(","))
                        paciente_actual = buscar(id_input.value)

                        if not paciente_actual:
                            result_label.text = "⚠️ Paciente no encontrado"
                            return

                        campos_validos = {k for k in paciente_actual.keys() if k != "ID"}
                        nuevos_datos = {k: v for k, v in nuevos_datos_raw.items() if k in campos_validos}
                        campos_invalidos = [k for k in nuevos_datos_raw if k not in campos_validos]

                        if not nuevos_datos:
                            result_label.text = "⚠️ Ningún campo válido para actualizar."
                            return

                        r = actualizar(id_input.value, nuevos_datos)
                        if r.matched_count:
                            paciente_actualizado = buscar(id_input.value)
                            if paciente_actualizado:
                                if archivo_original['nombre']:
                                    nombre_base = os.path.splitext(archivo_original['nombre'])[0]
                                    nombre_actualizado = f"{nombre_base}_actualizado"
                                else:
                                    nombre_actualizado = f"paciente{id_input.value}_actualizado.hl7"

                                paciente_actualizado_full = {
                                    'archivo': nombre_actualizado,
                                    'datos': paciente_actualizado,
                                    'datos_completos': paciente_actualizado
                                }

                                # Solo se actualiza el PID, MSH y OBR se mantienen
                                actualizar_hl7_txt(paciente_actualizado_full, 'salida',msh,obr,obx)

                                msg = f"🔄 Paciente actualizado. {nombre_actualizado}"
                                if campos_invalidos:
                                    msg += f"\n⚠️ Campos ignorados: {', '.join(campos_invalidos)}"
                                result_label.text = msg
                                info_paciente.text = "\n".join(f"{k}: {v}" for k, v in paciente_actualizado.items())
                            else:
                                result_label.text = "⚠️ No se pudo recuperar el paciente actualizado"
                        else:
                            result_label.text = "⚠️ Paciente no encontrado"
                    except Exception as e:
                        result_label.text = f"❌ Error: {str(e)}"

                ui.button("Actualizar", on_click=actualizar_paciente)
            else:
                info_paciente.text = "⚠️ Paciente no encontrado"

        cargar_button = ui.button("Cargar datos", on_click=cargar_y_mostrar)

        info_paciente
        nuevos_input
        ui.button("Cerrar", on_click=dialog.close)
        result_label

    dialog.open()
"""
def abrir_actualizacion():
    with ui.dialog() as dialog:
        with ui.card().style("width: 700px; height: 500px; overflow: auto; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px;"):
            ui.label("Actualizar paciente").style("margin-bottom: 20px;")
            
            # Campo para ingresar ID del paciente 
            id_input = ui.input("ID del paciente").style("width: 100%; height: 40px; font-size: 16px; margin-bottom: 20px;")
            
            # Etiqueta para mostrar la información del paciente o mensajes
            result_label = ui.label().style("margin-bottom: 20px;")

            # Campo para ingresar los nuevos datos 
            nuevos_input = ui.input("Nuevos datos (ej: Nombre:Juan,Edad:30)").style("width: 100%; height: 40px; font-size: 16px; margin-bottom: 20px;")

            # Función para buscar paciente por ID
            def buscar_paciente():
                paciente = buscar(id_input.value)
                print(f"Buscando paciente con ID: {id_input.value}")  
                if paciente:
                    # Si el paciente es encontrado, mostrar sus datos
                    paciente_info = "\n".join(f"{k}: {v}" for k, v in paciente.items())
                    result_label.text = f"👤 Paciente encontrado:\n{paciente_info}"
                else:
                    result_label.text = "⚠️ Paciente no encontrado"

            # Función para actualizar los datos del paciente
            def actualizar_paciente():
                try:
                    # Asegúrate de que los nuevos datos no estén vacíos
                    if not nuevos_input.value.strip():
                        result_label.text = "⚠️ Por favor ingrese nuevos datos en el formato correcto (ej: Nombre:Juan,Edad:30)."
                        return
                    
                    # Convertir los nuevos datos en un diccionario
                    nuevos_datos = dict(pair.split(":") for pair in nuevos_input.value.split(","))
                    print(f"Nuevos datos para actualizar: {nuevos_datos}") 
                    
                    # Intentar actualizar el paciente
                    r = actualizar(id_input.value, nuevos_datos)
                    if r.matched_count:
                        result_label.text = "🔄 Paciente actualizado correctamente."
                    else:
                        result_label.text = "⚠️ Error al actualizar el paciente."
                except Exception as e:
                    result_label.text = f"❌ Error: {str(e)}"
                    print(f"Error al actualizar: {str(e)}")  

            # Contenedor para los botones, alineados en el centro de la ventana
            with ui.row().style("width: 100%; justify-content: center; gap: 10px; margin-top: 20px;"):
                # Botón de "Buscar"
                ui.button("Buscar", on_click=buscar_paciente).style("width: 100px; height: 40px;")
                
                # Botón de "Actualizar"
                actualizar_button = ui.button("Actualizar", on_click=actualizar_paciente).style("width: 100px; height: 40px;")
                
                # Botón de "Cerrar"
                ui.button("Cerrar", on_click=dialog.close).style("width: 100px; height: 40px;")
        
    dialog.open()
"""
# --- Función para eliminar paciente ---
def abrir_eliminacion():
    with ui.dialog() as dialog, ui.card():
        ui.label("Eliminar paciente")
        id_input = ui.input("ID del paciente")

        def eliminar_paciente():
            r = eliminar(id_input.value)
            if r.deleted_count:
                # Crear un nuevo diálogo para mostrar el mensaje de eliminación exitosa con estilo
                with ui.dialog() as confirm_dialog:
                    confirm_dialog.classes('bg-white p-8 rounded-lg shadow-lg')  # Estilo personalizado
                    
                    with ui.column().classes('items-center'):  # Centra el contenido en la columna
                        ui.label("Paciente eliminado exitosamente.").classes('text-lg font-medium text-black-500')
                        ui.button("Cerrar", on_click=confirm_dialog.close).classes('mt-4')  # Botón debajo del texto

                confirm_dialog.open()  # Mostrar el mensaje de eliminación
            else:
                # Crear un nuevo diálogo para mostrar el mensaje de error con estilo
                with ui.dialog() as error_dialog:
                    error_dialog.classes('bg-white p-8 rounded-lg shadow-lg')  # Estilo personalizado
                    
                    with ui.column().classes('items-center'):  # Centra el contenido en la columna
                        ui.label("⚠️ Paciente no encontrado.").classes('text-lg font-medium text-red-500')
                        ui.button("Cerrar", on_click=error_dialog.close).classes('mt-4')  # Botón debajo del texto

                error_dialog.open()  # Mostrar el mensaje de error

        ui.button("Eliminar", on_click=eliminar_paciente)
        ui.button("Cerrar", on_click=dialog.close)

    dialog.open()

# --- Iniciar servidor ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
