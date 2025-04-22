import tkinter as tk
from tkinter import messagebox
from procesadorArchivos import leer_archivos
from mongoClient import insertar, buscar, actualizar, eliminar

def cargar_datos():
    datos = leer_archivos('data')
    pacientes_a_insertar = []

    for paciente in datos:
        paciente_data = paciente.get('datos', {})

        if 'ID' in paciente_data and 'Nombres' in paciente_data and 'Apellidos' in paciente_data:
            if buscar(paciente_data['ID']):
                print(f"🔁 Paciente con ID {paciente_data['ID']} ya existe.")
            else:
                pacientes_a_insertar.append(paciente_data)

    if pacientes_a_insertar:
        insertar(pacientes_a_insertar)
        messagebox.showinfo("Carga completa", f"{len(pacientes_a_insertar)} pacientes nuevos insertados.")
    else:
        messagebox.showinfo("Sin cambios", "No hay pacientes nuevos para insertar.")

def buscar_paciente():
    id_paciente = id_entry.get()
    paciente = buscar(id_paciente)
    if paciente:
        resultado.set(f"Paciente encontrado:\n{paciente}")
    else:
        resultado.set("Paciente no encontrado.")

def actualizar_paciente():
    id_paciente = id_entry.get()
    nuevos_datos = datos_entry.get()
    nuevos = dict(pair.split(":") for pair in nuevos_datos.split(","))
    r = actualizar(id_paciente, nuevos)
    if r.matched_count:
        messagebox.showinfo("Actualizado", "Paciente actualizado.")
    else:
        messagebox.showwarning("Error", "Paciente no encontrado.")

def eliminar_paciente():
    id_paciente = id_entry.get()
    r = eliminar(id_paciente)
    if r.deleted_count:
        messagebox.showinfo("Eliminado", "Paciente eliminado.")
    else:
        messagebox.showwarning("Error", "Paciente no encontrado.")

# --- GUI Setup ---
root = tk.Tk()
root.title("HIS - Interfaz gráfica")
root.geometry("600x400")

tk.Button(root, text="Cargar datos desde archivos", command=cargar_datos).pack(pady=5)

tk.Label(root, text="ID del paciente").pack()
id_entry = tk.Entry(root)
id_entry.pack()

tk.Label(root, text="Nuevos datos (Nombre:Juan,Edad:40)").pack()
datos_entry = tk.Entry(root)
datos_entry.pack()

tk.Button(root, text="Buscar paciente", command=buscar_paciente).pack(pady=5)
tk.Button(root, text="Actualizar paciente", command=actualizar_paciente).pack(pady=5)
tk.Button(root, text="Eliminar paciente", command=eliminar_paciente).pack(pady=5)

resultado = tk.StringVar()
tk.Label(root, textvariable=resultado, wraplength=500, justify="left").pack(pady=10)

tk.Button(root, text="Salir", command=root.quit).pack(pady=5)

root.mainloop()
