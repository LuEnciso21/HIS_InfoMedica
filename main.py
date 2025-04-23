from nicegui import ui
from procesadorArchivos import leer_archivos
from mongoClient import insertar, buscar, actualizar, eliminar

# --- Etiqueta principal para mensajes globales ---
data_label = ui.label("").style("margin-top: 20px;")

# --- Página principal ---
@ui.page("/")
def main_page():
    ui.label("Sistema HIS - Gestión de Pacientes").classes("text-2xl mb-4")

    with ui.row():
        ui.button("📂 Cargar datos desde archivos", on_click=cargar_datos)
        ui.button("🔍 Buscar paciente", on_click=abrir_busqueda)
        ui.button("📝 Actualizar paciente", on_click=abrir_actualizacion)
        ui.button("🗑️ Eliminar paciente", on_click=abrir_eliminacion)

    ui.label().bind_text_from(data_label, 'value')

# --- Función para cargar archivos y agregar pacientes ---
def cargar_datos():
    datos = leer_archivos('data')
    pacientes_a_insertar = []

    for paciente in datos:
        paciente_data = paciente.get('datos', {})
        if 'ID' in paciente_data and 'Nombres' in paciente_data and 'Apellidos' in paciente_data:
            existente = buscar(paciente_data['ID'])
            if not existente:
                pacientes_a_insertar.append(paciente_data)

    if pacientes_a_insertar:
        insertar(pacientes_a_insertar)
        data_label.value = f"📂 {len(pacientes_a_insertar)} pacientes nuevos insertados."
    else:
        data_label.value = "⚠️ No hay pacientes nuevos para insertar."

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
        nuevos_input = ui.input("Nuevos datos (ej: Nombre:Juan,Edad:30)")
        result_label = ui.label()

        def actualizar_paciente():
            try:
                nuevos_datos = dict(pair.split(":") for pair in nuevos_input.value.split(","))
                r = actualizar(id_input.value, nuevos_datos)
                if r.matched_count:
                    result_label.text = "🔄 Paciente actualizado."
                else:
                    result_label.text = "⚠️ Paciente no encontrado"
            except:
                result_label.text = "❌ Formato incorrecto"

        ui.button("Actualizar", on_click=actualizar_paciente)
        ui.button("Cerrar", on_click=dialog.close)

    dialog.open()

# --- Función para eliminar paciente ---
def abrir_eliminacion():
    with ui.dialog() as dialog, ui.card():
        ui.label("Eliminar paciente")
        id_input = ui.input("ID del paciente")
        result_label = ui.label()

        def eliminar_paciente():
            r = eliminar(id_input.value)
            if r.deleted_count:
                result_label.text = "🗑️ Paciente eliminado."
            else:
                result_label.text = "⚠️ Paciente no encontrado"

        ui.button("Eliminar", on_click=eliminar_paciente)
        ui.button("Cerrar", on_click=dialog.close)

    dialog.open()

# --- Iniciar servidor ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
