#Hecho por Stella Maris Pérez Cadena.
#Corregido por Santiago Emmanuel Morales Bautista.
#Importamos re para validaciones por medio de expresiones regulares.
import re
# Función para validar el formato de correo electrónico
def validar_correo(correo):
    correo_patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(correo_patron, correo))
while True:
    correo = input("Ingrese el correo electrónico del cliente: ").strip()
    if not correo:
        print("\n*****ERROR: El campo de correo electrónico no puede estar en blanco.*****")
    elif not validar_correo(correo):
        print("\n*****ERROR: La dirección de correo electrónico no es válida. Debe seguir el formato: usuario@organización.tipo*****")
    else:
        print("Correo validado")
        break