from procesadorArchivos import leer_archivos
from mongoClient import insertar, buscar, actualizar, eliminar
# from hl7_generator import generar_hl7
import os

def menu():
    while True:
        print("\n--- HIS - Menú ---")
        print("1. Cargar datos desde archivos")
        print("2. Agregar paciente manualmente")
        print("3. Buscar paciente")
        print("4. Actualizar paciente")
        print("5. Eliminar paciente")
        print("6. Salir")
        opcion = input("Opción: ")

        if opcion == '1':
            datos = leer_archivos('data')
            insertar(datos)
            print("📂 Datos insertados desde archivos.")

        elif opcion == '2':
            id = input("Ingrese el ID del paciente: ")
            nombre = input("Ingrese el nombre del paciente: ")
            paciente = {"ID": id, "Nombre": nombre}
            insertar(paciente)
            print("✅ Paciente agregado manualmente.")

        elif opcion == '3':
            id = input("ID del paciente: ")
            paciente = buscar(id)
            if paciente:
                print("👤 Paciente encontrado:", paciente)
                ruta = f"hl7_data/{id}.txt"
                # generar_hl7(paciente, ruta)
                print(f"📄 HL7 guardado en {ruta}")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '4':
            id = input("ID del paciente: ")
            nuevos = input("Nuevos datos (ej: Nombre:Juan,Edad:30): ")
            nuevos_datos = dict(pair.split(":") for pair in nuevos.split(","))
            r = actualizar(id, nuevos_datos)
            if r.matched_count:
                print("🔄 Paciente actualizado.")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '5':
            id = input("ID del paciente: ")
            r = eliminar(id)
            if r.deleted_count:
                print("🗑️ Paciente eliminado.")
            else:
                print("⚠️ Paciente no encontrado")

        elif opcion == '6':
            print("👋 Hasta luego.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu()
