import datetime	# Importamos el modulo datetime para el manejo de fechas.
import csv	#Importamos csv para poder guardar e importar el estado.
import re	#Importamos re para validaciones por medio de expresiones regulares.
import os	#Importamos os para gestionar archivos y directorios.
from tabulate import tabulate	#Tuvimos que instalar la biblioteca tabulate.
import xlsxwriter	#Importamos xlsxwriter para exportar archivos a Excel.

# Lista para almacenar las notas.
notas = []

# Función para generar automáticamente el folio de cada nota.
def generar_folio():
    if not notas:
        return 1
    else:
        return max(nota['folio'] for nota in notas) + 1
    
# Función para validar el formato de RFC persona física.
def validar_rfc_persona_fisica(rfc):
    rfc_patron_fisica = r'^[A-Z]{4}\d{6}[A-Z\d]{3}$'
    return bool(re.match(rfc_patron_fisica, rfc))

# Función para validar el formato de RFC persona moral.
def validar_rfc_persona_moral(rfc):
    rfc_patron_moral = r'^[A-Z]{3}\d{6}[A-Z\d]{3}$'
    return bool(re.match(rfc_patron_moral, rfc))

# Función para validar el formato de correo electrónico.
def validar_correo(correo):
    correo_patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(correo_patron, correo))

# Función para registrar una nueva nota.
def registrar_nota():
    try:
        folio = generar_folio()
        while True:
            fecha = input("Ingrese la fecha con el siguiente formato: DD-MM-YYYY ")
            try:
                fecha = datetime.datetime.strptime(fecha, "%d-%m-%Y")
                if fecha > datetime.datetime.now():# Verificar que la fecha ingresada no sea superior a la actual.
                    # Utilizamos .now(), ya que este te regresa los valores con todo y hora y .today() es solo la fecha.
                    # Mas que nada por si mas adelante nos hace consultar notas del mismo día pero diferente hora.
                    print("\n*****Error: No se puede ingresar una nota con fecha futura.*****")
                else:
                    break
            except ValueError:
                print("\n*****Error: Ingrese una fecha válida en formato DD-MM-YYYY.*****")

        while True:
            tipo_persona = input("Ingrese el tipo de persona (F para física, M para moral): ").strip().upper()
            if tipo_persona not in ('F', 'M'):
                print("\n*****Error: Ingrese 'F' para persona física o 'M' para persona moral.*****")
            else:
                break

        while True:
            cliente = input("Ingrese el nombre del cliente: ")
            if not cliente.strip():
                print("\n*****Error: El nombre del cliente no puede estar en blanco.*****")
            elif not any(char.isalpha() for char in cliente):
                print("\n*****Error: El nombre del cliente debe contener al menos una letra.*****")
            else:
                break

        while True:
            rfc = input("Ingrese el RFC del cliente: ").strip().upper()
            if tipo_persona.upper() == 'F':
                if not validar_rfc_persona_fisica(rfc):
                    print("\n*****ERROR: El formato del RFC para persona física es incorrecto.*****")
                else:
                    break
            elif tipo_persona.upper() == 'M':
                if not validar_rfc_persona_moral(rfc):
                    print("\n*****ERROR: El formato del RFC para persona moral es incorrecto.*****")
                else:
                    break
            else:
                print("\n*****ERROR: Opción no válida. Por favor, seleccione una opción válida.*****")

        while True:
            correo = input("Ingrese el correo electrónico del cliente: ").strip()
            if not correo:
                print("\n*****ERROR: El campo de correo electrónico no puede estar en blanco.*****")
            elif not validar_correo(correo):
                print("\n*****ERROR: La dirección de correo electrónico no es válida. Debe seguir el formato: usuario@dominio.com*****")
            else:
                break

        detalle = []

        while True:
            servicio = input("Ingrese el nombre del servicio (o 'fin' para terminar): ")
            if servicio.lower() == 'fin':
                if not detalle:
                    print("\n*****ERROR: Debe ingresar al menos un servicio y su costo mayor a 0.*****")
                    continue
                else:
                    break

            if not servicio.strip():
                print("\n*****ERROR: El nombre del servicio no puede estar en blanco.*****")
                continue

            while True:
                try:
                    costo = float(input("Ingrese el costo del servicio: "))
                    if costo <= 0:
                        print("*****ERROR: El costo del servicio debe ser mayor a 0.*****")
                    else:
                        break
                except ValueError:
                    print("\n*****ERROR: Ingrese un costo válido (número decimal).*****")

            detalle.append({'servicio': servicio, 'costo': costo})

        total = sum(servicio['costo'] for servicio in detalle)

        print("\nNota:")
        print(f"Folio: {folio}")
        print(f"Fecha: {fecha.strftime('%d-%m-%Y')}")
        print(f"Tipo de Persona: {'Física' if tipo_persona == 'F' else 'Moral'}")
        print(f"Cliente: {cliente}")
        print(f"RFC: {rfc}")
        print(f"Correo electrónico: {correo}")
        print("\nServicios y Costos:")
        for servicio in detalle:
            print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
        print(f"Total de la Nota: {total}")

        notas.append({'folio': folio, 'fecha': fecha.strftime("%d-%m-%Y"), 'tipo_persona': tipo_persona, 'cliente': cliente, 'rfc': rfc, 'correo': correo, 'detalle': detalle, 'total': total})

        print(f"Nota registrada con folio {folio}")
    except ValueError:
        print("\n*****ERROR: Ingrese un costo válido (número decimal).*****")

# Función para realizar consultas y reportes.
def consultar_notas():
    while True:
        print("\nConsultas y Reportes:")
        print("1. Consulta por período")
        print("2. Consulta por folio")
        print("3. Consulta por cliente")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            consulta_por_periodo()
        elif opcion == '2':
            consulta_por_folio()
        elif opcion == '3':
            consulta_por_cliente()
        elif opcion == '4':
            print("\nRegresando al menú principal...")
            break
        else:
            print("\nOpción no válida. Por favor, seleccione una opción válida.")

#Función para consultas por período.
def consulta_por_periodo():
    print("\nConsulta por período")
    while True:
        while True:
            try:
                fecha_inicial = input("Ingrese la fecha inicial (DD-MM-YYYY) o presione Enter para omitirla: ")
                if not fecha_inicial:
                    fecha_inicial = datetime.datetime(2000, 1, 1)  # Fecha por defecto: 01-01-2000
                    break
                else:
                    fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d-%m-%Y")
                    break
            except ValueError:
                print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")

        while True:
            try:
                fecha_final = input("Ingrese la fecha final (DD-MM-YYYY) o presione Enter para omitirla: ")
                if not fecha_final:
                    fecha_final = datetime.datetime.now()
                    break
                else:
                    fecha_final = datetime.datetime.strptime(fecha_final, "%d-%m-%Y")
                    break
            except ValueError:
                print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")

        if fecha_final < fecha_inicial:
            print("\n*****ERROR: La fecha final debe ser posterior o igual a la fecha inicial.*****")
        else:
            break

    resultado = []

    for nota in notas:
        fecha_nota = datetime.datetime.strptime(nota['fecha'], "%d-%m-%Y")
        if fecha_inicial <= fecha_nota <= fecha_final:
            resultado.append(nota)

    if resultado:
        print("\nNotas encontradas en el período seleccionado:")
        for nota in resultado:
            print(f"Folio: {nota['folio']}")
            print(f"Fecha: {nota['fecha']}")
            print(f"Tipo de Persona: {'Física' if nota['tipo_persona'] == 'F' else 'Moral'}")
            print(f"Cliente: {nota['cliente']}")
            print(f"RFC: {nota['rfc']}")
            print(f"Correo electrónico: {nota['correo']}")
            print("Servicios y Costos:")
            for servicio in nota['detalle']:
                print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
            print(f"Total de la Nota: {nota['total']}")
    else:
        print("\nNo se encontraron notas en el período seleccionado.")
        
#Función para consultas por folio.
def consulta_por_folio():
    while True:
        try:
            folio = int(input("\nIngrese el folio de la nota a consultar: "))
            nota_encontrada = buscar_nota_por_folio(folio)
            if nota_encontrada:
                print("\nNota encontrada:")
                # Imprimir la información de la nota directamente
                print(f"Folio: {nota_encontrada['folio']}")
                print(f"Fecha: {nota_encontrada['fecha']}")
                print(f"Tipo de Persona: {'Física' if nota_encontrada['tipo_persona'] == 'F' else 'Moral'}")
                print(f"Cliente: {nota_encontrada['cliente']}")
                print(f"RFC: {nota_encontrada['rfc']}")
                print(f"Correo electrónico: {nota_encontrada['correo']}")
                print("Servicios y Costos:")
                for servicio in nota_encontrada['detalle']:
                    print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
                print(f"Total de la Nota: {nota_encontrada['total']}")
            else:
                print("\n*****ERROR: La nota no existe o está cancelada.*****")
            break
        except ValueError:
            print("\n*****ERROR: Ingrese un número de folio válido.*****")

#Función para buscar una nota en la lista de notas almacenadas en el programa utilizando su número de folio como referencia. 
def buscar_nota_por_folio(folio):
    for nota in notas:
        if nota['folio'] == folio:
            return nota
    return None

# Función para consultar por cliente.
def consulta_por_cliente():
    print("\nConsulta por cliente")
    
    # Crear un diccionario para almacenar los RFCs únicos y asignar folios consecutivos
    rfc_dict = {}
    folio = 1

    # Llenar el diccionario con RFCs únicos y asignar folios
    for nota in notas:
        if nota['rfc'] not in rfc_dict:
            rfc_dict[nota['rfc']] = folio
            folio += 1

    headers = ["Folio", "RFC"]
    tabla_rfcs = []

    # Crear una tabla de RFCs ordenados alfabéticamente con folios consecutivos
    for rfc, folio in sorted(rfc_dict.items(), key=lambda item: item[0]):
        tabla_rfcs.append([folio, rfc])

    print("Listado de RFCs:")
    print(tabulate(tabla_rfcs, headers=headers, tablefmt="grid"))

    while True:
        try:
            opcion_rfc = input("Ingrese el folio del RFC a consultar (o 'FIN' para salir): ")

            if opcion_rfc.upper() == 'FIN':
                break

            opcion_rfc = int(opcion_rfc)

            if opcion_rfc < 1 or opcion_rfc > len(rfc_dict):
                print("Opción inválida. Ingrese un número de RFC válido.")
                continue

            rfc_seleccionado = None

            # Encontrar el RFC correspondiente al folio seleccionado
            for rfc, folio in sorted(rfc_dict.items(), key=lambda item: item[0]):
                if folio == opcion_rfc:
                    rfc_seleccionado = rfc
                    break

            # Filtrar las notas del cliente seleccionado por su RFC
            notas_cliente = [nota for nota in notas if nota['rfc'] == rfc_seleccionado]

            headers = ["Folio", "Fecha", "Total"]
            tabla_notas_cliente = []

            # Crear una tabla con las notas del cliente
            for nota in notas_cliente:
                tabla_notas_cliente.append([nota['folio'], nota['fecha'], nota['total']])

            print("\nNotas del cliente:")
            print(tabulate(tabla_notas_cliente, headers=headers, tablefmt="grid"))

            promedio_notas_cliente = sum(nota['total'] for nota in notas_cliente) / len(notas_cliente)
            print(f"Monto promedio de las notas del cliente: {promedio_notas_cliente:.2f}")

            exportar_excel = input("¿Desea exportar esta información a un archivo Excel? (S/N): ")
            if exportar_excel.upper() == 'S':
                exportar_informacion_excel(rfc_seleccionado, notas_cliente)

        except ValueError:
            print("Error: Ingrese un número entero o 'FIN' para salir.")

# Función para exportar la información de un cliente a un archivo Excel
def exportar_informacion_excel(cliente, notas_cliente):
    try:
        # Nombre del archivo Excel
        fecha_emision = datetime.datetime.now().strftime("%d-%m-%Y")  # Cambio de formato a día-mes-año
        nombre_archivo = f"Informacion_Cliente_{cliente}_{fecha_emision}.xlsx"

        # Crear un libro de trabajo y una hoja de trabajo
        libro_trabajo = xlsxwriter.Workbook(nombre_archivo)
        hoja_trabajo = libro_trabajo.add_worksheet()

        # Definir formatos
        formato_encabezado = libro_trabajo.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'yellow', 'border': 1})
        formato_fecha = libro_trabajo.add_format({'num_format': 'dd-mm-yyyy'})  
        formato_numeros = libro_trabajo.add_format({'num_format': '#,##0.00'})

        # Escribir los encabezados
        hoja_trabajo.write('A1', 'Folio', formato_encabezado)
        hoja_trabajo.write('B1', 'Fecha', formato_encabezado)
        hoja_trabajo.write('C1', 'Total', formato_encabezado)

        # Escribir los datos de las notas
        fila = 1
        columna = 0
        for nota in notas_cliente:
            fila += 1
            hoja_trabajo.write(fila, columna, nota['folio'])
            hoja_trabajo.write(fila, columna + 1, datetime.datetime.strptime(nota['fecha'], "%d-%m-%Y"), formato_fecha)
            hoja_trabajo.write(fila, columna + 2, nota['total'], formato_numeros)

        # Autoajustar las columnas
        hoja_trabajo.set_column('A:C', 15)

        # Cerrar el libro de trabajo
        libro_trabajo.close()

        print(f"La información del cliente '{cliente}' ha sido exportada a '{nombre_archivo}'.")

    except Exception as e:
        print(f"Error al exportar la información a Excel: {str(e)}")
        
# Función para cancelar una nota.
def cancelar_nota():
    folio = input("\nIngrese el folio de la nota a cancelar: ")
    nota_a_cancelar = None

    for nota in notas:
        if str(nota['folio']) == folio:
            nota_a_cancelar = nota
            break

    if nota_a_cancelar:
        if 'cancelada' not in nota_a_cancelar:
            # Mostrar el detalle de la nota
            print("\nDetalle de la nota a cancelar:")
            print(f"Folio: {nota_a_cancelar['folio']}")
            print(f"Fecha: {nota_a_cancelar['fecha']}")
            print(f"Tipo de Persona: {'Física' if nota_a_cancelar['tipo_persona'] == 'F' else 'Moral'}")
            print(f"Cliente: {nota_a_cancelar['cliente']}")
            print(f"RFC: {nota_a_cancelar['rfc']}")
            print(f"Correo electrónico: {nota_a_cancelar['correo']}")
            print("Servicios y Costos:")
            for servicio in nota_a_cancelar['detalle']:
                print(f"Servicio: {servicio['servicio']}, Costo: {servicio['costo']}")
            print(f"Total de la Nota: {nota_a_cancelar['total']}")

            confirmacion = input(f"\n¿Está seguro de que desea cancelar la nota con folio {folio}? (S/N): ")
            if confirmacion.strip().upper() == 'S':
                nota_a_cancelar['cancelada'] = True
                print(f"\nNota con folio {folio} cancelada.")
            elif confirmacion.strip().upper() == 'N':
                print("\nOperación de cancelación cancelada.")
            else:
                print("\nOpción no válida. Por favor, ingrese 'S' para confirmar o 'N' para cancelar.")
        else:
            print(f"\nLa nota con folio {folio} ya está cancelada.")
    else:
        print("\n*****ERROR: No se encontró ninguna nota con el folio proporcionado o la nota ya está cancelada.*****")

# Función para recuperar una nota cancelada.
def recuperar_nota():
    notas_canceladas = [nota for nota in notas if 'cancelada' in nota]

    if not notas_canceladas:
        print("\nNo hay notas canceladas para recuperar.")
        return

    # Mostrar un listado tabular de las notas canceladas (sin su detalle)
    headers = ["Folio", "Fecha", "Cliente"]
    tabla_notas_canceladas = [[nota['folio'], nota['fecha'], nota['cliente']] for nota in notas_canceladas]
    print("\nListado de notas canceladas:")
    print(tabulate(tabla_notas_canceladas, headers=headers, tablefmt="grid"))

    while True:
        folio = input("\nIngrese el folio de la nota que desea recuperar o 'N' para cancelar la operación: ")

        if folio.upper() == 'N':
            print("\nOperación de recuperación cancelada.")
            return

        try:
            folio = int(folio)
            nota_a_recuperar = next((nota for nota in notas_canceladas if nota['folio'] == folio), None)

            if nota_a_recuperar:
                # Mostrar el detalle de la nota
                print("\nDetalle de la nota a recuperar:")
                mostrar_notas([nota_a_recuperar])

                confirmacion = input(f"\n¿Está seguro de que desea recuperar la nota con folio {folio}? (S/N): ")
                if confirmacion.strip().upper() == 'S':
                    nota_a_recuperar.pop('cancelada')  # Eliminar la marca de cancelada
                    print(f"\nNota con folio {folio} recuperada.")
                elif confirmacion.strip().upper() == 'N':
                    print("\nOperación de recuperación cancelada.")
                else:
                    print("\nOpción no válida. Por favor, ingrese 'S' para confirmar o 'N' para cancelar.")
            else:
                print("\n*****ERROR: No se encontró ninguna nota cancelada con el folio proporcionado.*****")
        except ValueError:
            print("\n*****ERROR: Ingrese un número de folio válido o 'N' para cancelar la operación.*****")

# Función para guardar el estado de la aplicación en un archivo CSV.
def guardar_estado():
    try:
        nombre_archivo = "estado_app.csv"
        with open(nombre_archivo, mode='w', newline='') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)

            # Escribir las notas en el archivo CSV
            for nota in notas:
                escritor_csv.writerow([nota['folio'], nota['fecha'], nota['tipo_persona'], nota['cliente'], nota['rfc'], nota['correo'], nota['total']])

        print(f"El estado de la aplicación ha sido guardado en el archivo '{nombre_archivo}'.")
    except Exception as e:
        print(f"Error al guardar el estado de la aplicación: {str(e)}")

# Función para cargar el estado de la aplicación desde un archivo CSV.
def cargar_estado():
    nombre_archivo = "estado_app.csv"
    if os.path.isfile(nombre_archivo):
        with open(nombre_archivo, mode='r', newline='') as archivo_csv:
            lector_csv = csv.reader(archivo_csv)
            notas.clear()  # Limpiar la lista de notas antes de cargar el estado

            # Leer las filas del archivo CSV y cargar las notas
            for fila in lector_csv:
                folio, fecha, tipo_persona, cliente, rfc, correo, total = fila
                notas.append({
                    'folio': int(folio),
                    'fecha': fecha,
                    'tipo_persona': tipo_persona,
                    'cliente': cliente,
                    'rfc': rfc,
                    'correo': correo,
                    'total': float(total)
                })

        print(f"El estado de la aplicación ha sido cargado desde el archivo '{nombre_archivo}'.")
    else:
        print("No se encontró un archivo de estado previo. Se parte de un estado inicial vacío.")

#Función para el menú principal del programa.
def main():
    cargar_estado()
    print("\nBienvenido al Taller Mecánico Morales.")
    while True:
        print("\nMenú Principal - Sistema de notas:")
        print("1. Registrar una nota nueva.")
        print("2. Consultas y reportes.")
        print("3. Cancelar una nota.")
        print("4. Recuperar una nota.")
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
            confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
            while confirmacion.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion = input("¿Está seguro que desea salir? (S/N): ")
                
            if confirmacion_salir.upper() == 'S':
                guardar_estado()
                print("\nSaliendo del programa...")
                break
            elif confirmacion_salir.upper() == 'N':
                print("\nRedirigiendo al menú principal...")
                continue
        else:
            print("\nOpción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()

