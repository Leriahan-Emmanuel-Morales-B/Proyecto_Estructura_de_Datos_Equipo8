# Importamos el modulo datetime para el manejo de fechas.
import datetime

# Para este paso tuve que instalar la biblioteca 'tabulate'.
# Importamos la función tabulate
from tabulate import tabulate  

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
                if fecha > datetime.datetime.now():
                    print("Error: No se puede ingresar una nota con fecha futura.")
                else:
                    break
            except ValueError:
                print("Error: Ingrese una fecha válida en formato DD-MM-YYYY.")

        while True:
            cliente = input("Ingrese el nombre del cliente: ")
            if not cliente.strip():
                print("Error: El nombre del cliente no puede estar en blanco.")
            elif not any(char.isalpha() for char in cliente):
                print("Error: El nombre del cliente debe contener al menos una letra.")
            else:
                break

        detalle = []

        while True:
            servicio = input("Ingrese el nombre del servicio (o 'fin' para terminar): ")
            if servicio.lower() == 'fin':
                if not detalle:
                    print("Error: Debe ingresar al menos un servicio y su costo mayor a 0.")
                    continue
                else:
                    break

            if not servicio.strip():
                print("Error: El nombre del servicio no puede estar en blanco.")
                continue

            while True:
                try:
                    costo = float(input("Ingrese el costo del servicio: "))
                    if costo <= 0:
                        print("Error: El costo del servicio debe ser mayor a 0.")
                    else:
                        break
                except ValueError:
                    print("Error: Ingrese un costo válido (número decimal).")

            detalle.append({'servicio': servicio, 'costo': costo})

        total = sum(servicio['costo'] for servicio in detalle)

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
        while True:
            try:
                fecha_inicial = input("Ingrese la fecha inicial (DD-MM-YYYY): ")
                fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d-%m-%Y")
                break
            except ValueError:
                print("Error: Ingrese una fecha inicial válida en formato DD-MM-YYYY.")
        
        while True:
            try:
                fecha_final = input("Ingrese la fecha final (DD-MM-YYYY): ")
                fecha_final = datetime.datetime.strptime(fecha_final, "%d-%m-%Y")
                break
            except ValueError:
                print("Error: Ingrese una fecha final válida en formato DD-MM-YYYY.")
                
        if fecha_inicial > fecha_final:
            print("Error: La fecha inicial debe ser anterior a la fecha final.")
        else:
            break
    
    # Filtramos las notas canceladas.
    notas_en_periodo = [nota for nota in notas if fecha_inicial <= datetime.datetime.strptime(nota['fecha'], "%d-%m-%Y") <= fecha_final and (nota['total'] > 0 or sum(servicio['costo'] for servicio in nota['detalle']) > 0)]

    if not notas_en_periodo:
        print("No hay notas emitidas para el período especificado.")
    else:
        headers = ["Folio", "Fecha", "Cliente", "Total"]
        tabla_notas = []

        for nota in notas_en_periodo:
            if nota['total'] > 0:
                tabla_notas.append([nota['folio'], nota['fecha'], nota['cliente'], nota['total']])

        print("\nNotas en el período especificado:")
        print(tabulate(tabla_notas, headers=headers, tablefmt="grid"))

# Función para realizar una consulta por folio
def consulta_por_folio():
    print("\nConsulta por folio")
    while True:
        try:
            folio = input("Ingrese el folio de la nota a consultar: ")
            folio = int(folio)
            
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
        
            while True:
                desea_continuar = input("¿Desea realizar otra consulta por folio? (S/N): ")
                if desea_continuar.upper() == 'S':
                    break
                elif desea_continuar.upper() == 'N':
                    return
                else:
                    print("Opción no válida. Por favor, seleccione 'S' para realizar otra consulta por folio o 'N' para salir.")
        except ValueError:
            print("Error: Ingrese un número entero como folio.")

# Función para cancelar una nota
def cancelar_nota():
    while True:
        try:
            folio = input("Ingrese el folio de la nota a cancelar: ")
            folio = int(folio)
            
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
                
                confirmacion = input("¿Desea cancelar esta nota? (S/N): ")
                if confirmacion.upper() == 'S':
                    nota_encontrada['total'] = 0
                    print("Nota cancelada exitosamente.")
                elif confirmacion.upper() == 'N':
                    print("Operación de cancelación cancelada por el usuario.")
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")

            elif nota_encontrada is None:
                print("La nota indicada no existe o corresponde a una nota cancelada.")
            else:
                print("El folio ingresado no es válido.")
        
            while True:
                desea_continuar = input("¿Desea cancelar otra nota? (S/N): ")
                if desea_continuar.upper() == 'S':
                    break
                elif desea_continuar.upper() == 'N':
                    return
                else:
                    print("Opción no válida. Por favor, seleccione 'S' para cancelar otra nota o 'N' para salir.")
        except ValueError:
            print("Error: Ingrese un número entero como folio.")

# Función para recuperar una nota cancelada
def recuperar_nota():
    notas_canceladas = [nota for nota in notas if nota['total'] == 0]
    
    if not notas_canceladas:
        print("\nNo hay notas canceladas para recuperar.")
        return
    
    headers = ["Folio", "Fecha", "Cliente"]
    tabla_notas_canceladas = []

    for nota in notas_canceladas:
        tabla_notas_canceladas.append([nota['folio'], nota['fecha'], nota['cliente']])

    print("\nNotas Canceladas:")
    print(tabulate(tabla_notas_canceladas, headers=headers, tablefmt="grid"))

    while True:
        try:
            folio = input("Ingrese el folio de la nota a recuperar (o 'FIN' para salir): ")
            
            if folio.upper() == 'FIN':
                break
            
            folio = int(folio)
            
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
                print("\nDetalle de la nota:")
                for servicio in nota_encontrada['detalle']:
                    print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
                #print(f"Total de la Nota: {nota_encontrada['total']}")

                confirmacion = input("¿Desea recuperar esta nota? (S/N): ")
                if confirmacion.upper() == 'S':
                    nota_encontrada['total'] = sum(servicio['costo'] for servicio in nota_encontrada['detalle'])
                    print("Nota recuperada exitosamente.")
                elif confirmacion.upper() == 'N':
                    print("Operación de recuperación cancelada por el usuario.")
                else: 
                    print("Opción no válida. Por favor, seleccione una opción válida.")
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
            while confirmacion.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion = input("¿Está seguro que desea salir? (S/N): ")

            if confirmacion.upper() == 'S':
                print("Gracias por utilizar el sistema. Hasta luego.")
                break
            elif confirmacion.upper() == 'N':
                print("Redirigiendo al menú principal...")
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()

