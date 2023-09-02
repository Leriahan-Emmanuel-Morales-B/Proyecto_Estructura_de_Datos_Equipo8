# Definición de la estructura de datos
notas = []

# Función para generar automáticamente el folio de la nota
def generar_folio():
    if not notas:
        return 1
    else:
        return max(nota['folio'] for nota in notas) + 1

import datetime

# Función para registrar una nueva nota
def registrar_nota():
    try:
        folio = generar_folio()
        while True:
            fecha = input("Ingrese la fecha (DD-MM-YYYY): ")
            try:
                fecha = datetime.datetime.strptime(fecha, "%d-%m-%Y")
                if fecha > datetime.datetime.now():
                    print("Error: No se puede ingresar una nota con fecha futura.")
                else:
                    break
            except ValueError:
                print("Error: Ingrese una fecha válida en formato DD-MM-YYYY.")

        cliente = input("Ingrese el nombre del cliente: ")
        detalle = []

        # Validación para asegurarse de que se ingresen al menos un servicio y su costo mayor a 0
        while True:
            servicio = input("Ingrese el nombre del servicio (o 'fin' para terminar): ")
            if servicio.lower() == 'fin':
                if not detalle:
                    print("Error: Debe ingresar al menos un servicio y su costo mayor a 0.")
                    continue
                else:
                    break
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

        # Mostrar los servicios y costos ingresados
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
    while True:
        print("\nMenú Principal:")
        print("1. Registrar una nota")
        print("2. Consultas y reportes")
        print("3. Cancelar una nota")
        print("4. Recuperar una nota cancelada")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            registrar_nota()
        elif opcion == '5':
            confirmacion = input("¿Está seguro que desea salir? (S/N): ")
            if confirmacion.lower() == 's':
                break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
