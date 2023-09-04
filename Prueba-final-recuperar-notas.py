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

# Función para realizar consultas y reportes
def consultar_notas():
    while True:
        print("\nConsultas y Reportes:")
        print("1. Consulta por período")
        print("2. Consulta por folio")
        print("3. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            consulta_por_periodo()
        elif opcion == '2':
            consulta_por_folio()
        elif opcion == '3':
            print("Redirigiendo al menú principal...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

# Función para realizar una consulta por período
def consulta_por_periodo():
    print("\nConsulta por período")
    while True:
        try:
            fecha_inicial = input("Ingrese la fecha inicial (DD-MM-YYYY): ")
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d-%m-%Y")
            fecha_final = input("Ingrese la fecha final (DD-MM-YYYY): ")
            fecha_final = datetime.datetime.strptime(fecha_final, "%d-%m-%Y")
            
            if fecha_inicial > fecha_final:
                print("Error: La fecha inicial debe ser anterior a la fecha final.")
                continue
            
            # Filtrar las notas canceladas del resultado
            notas_en_periodo = [nota for nota in notas if fecha_inicial <= datetime.datetime.strptime(nota['fecha'], "%d-%m-%Y") <= fecha_final]

            if not notas_en_periodo:
                print("No hay notas emitidas para el período especificado.")
            else:
                print("\nNotas en el período especificado:")
                for nota in notas_en_periodo:
                    print("\nDatos de la nota:")
                    print(f"Folio: {nota['folio']}")
                    print(f"Fecha: {nota['fecha']}")
                    print(f"Cliente: {nota['cliente']}")
                    print("\nDetalle de la nota:")
                    for servicio in nota['detalle']:
                        print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
                    print(f"Total de la Nota: {nota['total']}")
            
            break
        except ValueError:
            print("Error: Ingrese fechas válidas en formato DD-MM-YYYY.")

# Función para realizar una consulta por folio
def consulta_por_folio():
    print("\nConsulta por folio")
    while True:
        try:
            folio = input("Ingrese el folio de la nota a consultar: ")
            folio = int(folio)  # Intenta convertir lo ingresado a un entero.
            
            nota_encontrada = None
            for nota in notas:
                if nota['folio'] == folio and nota['total'] > 0:
                    nota_encontrada = nota
                    break
        
            if nota_encontrada:
                print("\nDatos de la nota:")
                print(f"Folio: {nota_encontrada['folio']}")
                print(f"Fecha: {nota_encontrada['fecha']}")
                print(f"Cliente: {nota_encontrada['cliente']}")
                print("\nDetalle de la nota:")
                for servicio in nota_encontrada['detalle']:
                    print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
                print(f"Total de la Nota: {nota_encontrada['total']}")
            elif nota_encontrada is None:
                print("La nota indicada no existe o corresponde a una nota cancelada.")
            else:
                print("El folio ingresado no es válido.")
            
            # Validar que ingrese el usuario S o N en dado caso de que quiera realizar otra consulta.
            desea_continuar = input("¿Desea realizar otra consulta por folio? (s/n): ")
            while desea_continuar.lower() not in ('s', 'n'):
                print("Opción no válida. Por favor, seleccione 's' para continuar o 'n' para salir.")
                desea_continuar = input("¿Desea realizar otra consulta por folio? (s/n): ")

            if desea_continuar.lower() != 's':
                break

        except ValueError:
            print("Error: Ingrese un número entero como folio.")
            
# Función para cancelar una nota
def cancelar_nota():
    while True:
        try:
            folio = input("Ingrese el folio de la nota a cancelar: ")
            folio = int(folio)  # Intenta convertir la entrada a un entero
            
            nota_encontrada = None
            for nota in notas:
                if nota['folio'] == folio and nota['total'] > 0:
                    nota_encontrada = nota
                    break
        
            if nota_encontrada:
                print("\nDatos de la nota a cancelar:")
                print(f"Folio: {nota_encontrada['folio']}")
                print(f"Fecha: {nota_encontrada['fecha']}")
                print(f"Cliente: {nota_encontrada['cliente']}")
                print("\nDetalle de la nota:")
                for servicio in nota_encontrada['detalle']:
                    print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
                print(f"Total de la Nota: {nota_encontrada['total']}")
                
                confirmacion = input("¿Desea cancelar esta nota? (s/n): ")
                if confirmacion.lower() == 's':
                    nota_encontrada['total'] = 0  # Marcar la nota como cancelada (total en cero)
                    print("Nota cancelada exitosamente.")
                else:
                    print("Operación de cancelación cancelada por el usuario.")
            elif nota_encontrada is None:
                print("La nota indicada no existe o corresponde a una nota cancelada.")
            else:
                print("El folio ingresado no es válido.")
        
            desea_continuar = input("¿Desea cancelar otra nota? (s/n): ")
            if desea_continuar.lower() != 's':
                break
        except ValueError:
            print("Error: Ingrese un número entero como folio.")

# Función para recuperar una nota cancelada
def recuperar_nota():
    notas_canceladas = [nota for nota in notas if nota['total'] == 0]
    
    if not notas_canceladas:
        print("\nNo hay notas canceladas para recuperar.")
        return
    
    print("\nNotas Canceladas:")
    for nota in notas_canceladas:
        print(f"Folio: {nota['folio']}, Fecha: {nota['fecha']}, Cliente: {nota['cliente']}")
    
    while True:
        try:
            folio = input("Ingrese el folio de la nota a recuperar (o 'fin' para salir): ")
            
            if folio.lower() == 'fin':
                break
            
            folio = int(folio)  # Intenta convertir la entrada a un entero
            
            nota_encontrada = None
            for nota in notas_canceladas:
                if nota['folio'] == folio:
                    nota_encontrada = nota
                    break
            
            if nota_encontrada:
                print("\nDatos de la nota a recuperar:")
                print(f"Folio: {nota_encontrada['folio']}")
                print(f"Fecha: {nota_encontrada['fecha']}")
                print(f"Cliente: {nota_encontrada['cliente']}")
                
                confirmacion = input("¿Desea recuperar esta nota? (s/n): ")
                if confirmacion.lower() == 's':
                    nota_encontrada['total'] = sum(servicio['costo'] for servicio in nota_encontrada['detalle'])
                    print("Nota recuperada exitosamente.")
                else:
                    print("Operación de recuperación cancelada por el usuario.")
            elif nota_encontrada is None:
                print("La nota indicada no existe en la lista de notas canceladas.")
            else:
                print("El folio ingresado no es válido.")
        
        except ValueError:
            print("Error: Ingrese un número entero como folio.")
        
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
        elif opcion == '2':
            consultar_notas()
        elif opcion == '3':
            cancelar_nota()
        elif opcion == '4':
            recuperar_nota()
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