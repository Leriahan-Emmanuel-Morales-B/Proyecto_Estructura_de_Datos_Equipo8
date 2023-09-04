# Importamos el modulo datetime para el manejo de fechas.
import datetime

# Lista para almacenar las notas.
notas = []

# Función para generar automáticamente el folio de cada nota.
def generar_folio():
    if not notas:
        return 1
    else:
        return max(nota['folio'] for nota in notas) + 1

# Función para registrar una nueva nota.
def registrar_nota():
    try:
        folio = generar_folio()
        while True:
            fecha = input("Ingrese la fecha (DD-MM-YYYY): ")
            try:
                fecha = datetime.datetime.strptime(fecha, "%d-%m-%Y")
                if fecha > datetime.datetime.now():# Verificar que la fecha ingresada no sea superior a la actual.
                    # Utilizamos .now(), ya que este te regresa los valores con todo y hora y .today() es solo la fecha.
                    # Mas que nada por si mas adelante nos hace consultar notas del mismo día.
                    print("Error: No se puede ingresar una nota con fecha futura.")
                else:
                    break
            except ValueError:
                print("Error: Ingrese una fecha válida en formato DD-MM-YYYY.")

        while True:
            cliente = input("Ingrese el nombre del cliente: ")
            if not cliente.strip():  # Verificar si el nombre está en blanco o contiene solo espacios
                print("Error: El nombre del cliente no puede estar en blanco.")
            elif not any(char.isalpha() for char in cliente):
                print("Error: El nombre del cliente debe contener al menos una letra.")
            else:
                break

        detalle = []

        # Validación para asegurarse de que se ingresen al menos un servicio y su costo mayor a 0.
        while True:
            servicio = input("Ingrese el nombre del servicio (o 'fin' para terminar): ")
            if servicio.lower() == 'fin':
                if not detalle:
                    print("Error: Debe ingresar al menos un servicio y su costo mayor a 0.")
                    continue
                else:
                    break

            # Validar que el nombre del servicio no esté en blanco
            if not servicio.strip():
                print("Error: El nombre del servicio no puede estar en blanco.")
                continue

            while True:
                try:
                    costo = float(input("Ingrese el costo del servicio: "))
                    if costo <= 0:
                        print("Error: El costo del servicio debe ser mayor a 0.")
                    else:
                        break  # Salir del bucle si el costo es válido
                except ValueError:
                    print("Error: Ingrese un costo válido (número decimal).")

            detalle.append({'servicio': servicio, 'costo': costo})

        total = sum(servicio['costo'] for servicio in detalle)

        # Mostrar la nota en pantalla
        print("\nNota:")
        print(f"Folio: {folio}")
        print(f"Fecha: {fecha.strftime('%d-%m-%Y')}")
        print(f"Cliente: {cliente}")
        print("\nServicios y Costos:")
        for servicio in detalle:
            print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
        print(f"Total de la Nota: {total}")

        notas.append({'folio': folio, 'fecha': fecha.strftime("%d-%m-%Y"), 'cliente': cliente, 'detalle': detalle, 'total': total})

        print(f"Nota registrada con folio {folio}")
    except ValueError:
        print("Error: Ingrese un costo válido (número decimal).")
        
# Función principal del programa
def main():
    print("Bienvenido al Taller Mecánico Morales.")
    while True:
        print("\nMenú Principal - Sistema de notas:")
        print("1. Registrar una nota")
        print("2. Consultas y Reportes")
        print("3. Cancelar una nota")
        print("4. Recuperar una nota cancelada")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            registrar_nota()
        elif opcion == '5':
            confirmacion = input("¿Está seguro que desea salir? (S/N): ")
            while confirmacion.lower() not in ('s', 'n'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion = input("¿Está seguro que desea salir? (S/N): ")

            if confirmacion.lower() == 's':
                print("Gracias por utilizar el sistema. Hasta luego.")
                break
            elif confirmacion.lower() == 'n':
                print("Redirigiendo al menú principal...")
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()