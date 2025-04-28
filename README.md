# HIS_InfoMedica

# **Descripción**  
HIS_InfoMedica es una aplicación web diseñada para gestionar los datos de pacientes médicos de manera eficiente.  
Esta aplicación permite cargar, buscar, actualizar y eliminar información relacionada con los pacientes, integrando tanto una base de datos MongoDB como archivos HL7 para el manejo de datos de salud.  
El sistema está orientado a mejorar la accesibilidad y gestión de la información médica de manera intuitiva y rápida.

---

## **Requisitos**  
Python 3.12 o superior.

Dependencias de Python:
`
pip install pymongo
`
`
pip install nicegui
`

`
pip install flask
`

---
### Ejecutar la aplicación:

Para iniciar la aplicación, ejecuta el siguiente comando:

`
python main.py
`

---

## Funcionalidades

- **Paso inicial:** Cargar datos para subirlos a la base de datos y generar sus archivos HL7.

- **Buscar paciente:** Ingresa el ID del paciente para buscar su información en la base de datos.

- **Actualizar paciente:** Modifica los datos del paciente a través de un formulario.

- **Eliminar paciente:** Elimina el registro de un paciente de la base de datos.
