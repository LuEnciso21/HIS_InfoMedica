from procesadorArchivos import leer_archivos
from mongoClient import insertar, buscar, actualizar, eliminar
import os

def menu():
    while True:
        print("\n--- HIS - Menú ---")
        print("1. Cargar datos desde archivos")
        print("2. Buscar paciente")
        print("3. Actualizar paciente")
        print("4. Eliminar paciente")
        print("5. Salir")
        opcion = input("Opción: ")

        if opcion == '1':
            datos = leer_archivos('data')

            pacientes_a_insertar = []

            for paciente in datos:
                paciente_data = paciente.get('datos', {})

                if 'ID' in paciente_data and 'Nombres' in paciente_data and 'Apellidos' in paciente_data:
                    existente = buscar(paciente_data['ID'])

                    if existente:
                        print(f"🔁 Paciente con ID {paciente_data['ID']} ya existe. No se insertará.")
                    else:
                        pacientes_a_insertar.append(paciente_data)

            if pacientes_a_insertar:
                insertar(pacientes_a_insertar)
                print(f"📂 {len(pacientes_a_insertar)} pacientes nuevos insertados.")
            else:
                print("⚠️ No hay pacientes nuevos para insertar.")

        elif opcion == '2':
            id = input("ID del paciente: ")
            paciente = buscar(id)
            if paciente:
                print("👤 Paciente encontrado:", paciente)
                ruta = f"hl7_data/{id}.txt"
                # generar_hl7(paciente, ruta)
                #print(f"📄 HL7 guardado en {ruta}")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '3':
            id = input("ID del paciente: ")
            nuevos = input("Nuevos datos (ej: Nombre:Juan,Edad:30): ")
            nuevos_datos = dict(pair.split(":") for pair in nuevos.split(","))
            r = actualizar(id, nuevos_datos)
            if r.matched_count:
                print("🔄 Paciente actualizado.")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '4':
            id = input("ID del paciente: ")
            r = eliminar(id)
            if r.deleted_count:
                print("🗑️ Paciente eliminado.")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '5':
            print("👋 Hasta luego.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu()