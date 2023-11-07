# Módulos.
import sqlite3
import re
import csv
import datetime
from sqlite3 import Error
import sys
import pandas as pd

# Función para abrir la conexión a la base de datos
def abrir_conexion():
    try:
        conexion = sqlite3.connect("Evidencia_3_SEMB_1799759.db")
        cursor = conexion.cursor()
        return conexion, cursor
    except Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
        
# Función para crear tablas en la base de datos
def crear_tablas(cursor):
    try:
        # Tabla Clientes.
        cursor.execute("CREATE TABLE IF NOT EXISTS Clientes (Clave_Cliente INTEGER PRIMARY KEY NOT NULL, Nombre_Cliente TEXT NOT NULL, RFC TEXT NOT NULL, Correo TEXT NOT NULL)")
        # Tabla Servicios.
        cursor.execute("CREATE TABLE IF NOT EXISTS Servicios (Clave_Servicio INTEGER PRIMARY KEY NOT NULL, Nombre_Servicio TEXT NOT NULL, Costo REAL NOT NULL)")
        # Tabla Notas.
        cursor.execute("CREATE TABLE IF NOT EXISTS Notas (Folio INTEGER PRIMARY KEY NOT NULL, Fecha DATE timestamp NOT NULL, Clave_Cliente INTEGER NOT NULL, Monto REAL NOT NULL, Cancelada INTEGER DEFAULT 0, FOREIGN KEY (Clave_Cliente) REFERENCES Clientes(Clave_Cliente))")
        # Tabla Detalle Nota.
        cursor.execute("CREATE TABLE IF NOT EXISTS Detalles_Nota (Folio INTEGER, Clave_Servicio INTEGER, PRIMARY KEY (Folio, Clave_Servicio), FOREIGN KEY (Folio) REFERENCES Notas(Folio), FOREIGN KEY (Clave_Servicio) REFERENCES Servicios(Clave_Servicio))")

        print("Tablas creadas exitosamente.")

    except sqlite3.Error as e:
        print(f"Error al crear tablas en la base de datos: {e}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')

# Función para obtener la fecha actual en formato mm_dd_aaaa
def obtener_fecha_actual():
    fecha_actual = datetime.datetime.now()
    return fecha_actual.strftime("%m_%d_%Y")
      
# Función para registrar una nota
def registrar_nota(cursor):
    try:
        # Obtener la lista de clientes registrados
        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente FROM Clientes")
        clientes = cursor.fetchall()
        
        if not clientes:
            print("No hay clientes registrados. Registre un cliente antes de crear una nota.")
            return
        
        # Mostrar lista de clientes
        print("Clientes registrados:")
        for cliente in clientes:
            print(f"Clave: {cliente[0]}, Nombre: {cliente[1]}")
        
        # Solicitar clave de cliente
        clave_cliente = input("Ingrese la clave del cliente para la nota: ")
        
        if not clave_cliente.isdigit():
            print("Clave de cliente no válida.")
            return
        
        clave_cliente = int(clave_cliente)
        
        # Verificar si el cliente existe
        if (clave_cliente,) not in clientes:
            print("La clave de cliente no existe.")
            return
        
        # Obtener la lista de servicios registrados
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios")
        servicios = cursor.fetchall()
        
        if not servicios:
            print("No hay servicios registrados. Registre un servicio antes de crear una nota.")
            return
        
        # Mostrar lista de servicios
        print("Servicios registrados:")
        for servicio in servicios:
            print(f"Clave: {servicio[0]}, Nombre: {servicio[1]}, Costo: {servicio[2]}")
        
        # Solicitar detalles de la nota
        detalles = []
        while True:
            clave_servicio = input("Ingrese la clave del servicio (o 'T' para terminar): ")
            if clave_servicio == 'T':
                break
            
            if not clave_servicio.isdigit():
                print("Clave de servicio no válida.")
                continue
            
            clave_servicio = int(clave_servicio)
            
            # Verificamos si el servicio existe.
            servicio_existente = False
            for servicio in servicios:
                if clave_servicio == servicio[0]:
                    detalles.append(servicio)
                    servicio_existente = True
                    break
            
            if not servicio_existente:
                print("La clave de servicio no existe.")
        
        if not detalles:
            print("No se han agregado servicios a la nota.")
            return
        
        # Calculamos el monto total.
        monto_total = sum(servicio[2] for servicio in detalles)
        
        # Insertamos la nota en la base de datos.
        fecha_nota = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO Notas (Fecha, Clave_Cliente, Monto) VALUES (?, ?, ?)", (fecha_nota, clave_cliente, monto_total))
        nota_id = cursor.lastrowid
        
        # Insertamos los detalles de la nota.
        for servicio in detalles:
            cursor.execute("INSERT INTO Detalles_Nota (Clave_Nota, Clave_Servicio) VALUES (?, ?)", (nota_id, servicio[0]))
        
        print("Nota registrada con éxito.")
    
    except Exception as e:
        print(f"Error al registrar una nota: {str(e)}")

# Función para cancelar una nota
def cancelar_nota(cursor):
    try:
        folio_nota = input("Ingrese el folio de la nota a cancelar: ")
        
        if not folio_nota.isdigit():
            print("Folio de nota no válido.")
            return
        
        folio_nota = int(folio_nota)
        
        # Verificar si la nota existe
        cursor.execute("SELECT * FROM Notas WHERE Folio = ? AND Cancelada = 0", (folio_nota,))
        nota = cursor.fetchone()
        
        if nota:
            fecha, clave_cliente, monto = nota
            print(f"Detalles de la nota a cancelar:")
            print(f"Folio: {folio_nota}")
            print(f"Fecha: {fecha}")
            print(f"Clave de Cliente: {clave_cliente}")
            print(f"Monto: {monto}")
            
            confirmacion = input("¿Está seguro de que desea cancelar esta nota? (Sí/No): ").lower()
            if confirmacion == "si":
                cursor.execute("UPDATE Notas SET Cancelada = 1 WHERE Folio = ?", (folio_nota,))
                print(f"Nota {folio_nota} cancelada con éxito.")
            else:
                print(f"Nota {folio_nota} no ha sido cancelada.")
        else:
            print("La nota no existe o ya ha sido cancelada.")
    
    except Exception as e:
        print(f"Error al cancelar una nota: {str(e)}")

# Función para recuperar una nota
def recuperar_nota(cursor):
    try:
        # Obtener la lista de notas canceladas
        cursor.execute("SELECT Folio, Fecha, Clave_Cliente FROM Notas WHERE Cancelada = 1")
        notas_canceladas = cursor.fetchall()
        
        if not notas_canceladas:
            print("No hay notas canceladas para recuperar.")
            return
        
        # Mostrar lista de notas canceladas
        print("Notas canceladas:")
        for nota in notas_canceladas:
            print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Clave de Cliente: {nota[2]}")
        
        folio_recuperar = input("Ingrese el folio de la nota a recuperar (o 'q' para cancelar): ")
        
        if folio_recuperar == 'q':
            return
        
        if not folio_recuperar.isdigit():
            print("Folio de nota no válido.")
            return
        
        folio_recuperar = int(folio_recuperar)
        
        # Verificar si el folio existe
        for nota in notas_canceladas:
            if folio_recuperar == nota[0]:
                fecha, clave_cliente = nota[1], nota[2]
                print(f"Detalles de la nota a recuperar:")
                print(f"Folio: {folio_recuperar}")
                print(f"Fecha: {fecha}")
                print(f"Clave de Cliente: {clave_cliente}")
                
                confirmacion = input("¿Está seguro de que desea recuperar esta nota? (Sí/No): ").lower()
                if confirmacion == "si":
                    cursor.execute("UPDATE Notas SET Cancelada = 0 WHERE Folio = ?", (folio_recuperar,))
                    print(f"Nota {folio_recuperar} recuperada con éxito.")
                else:
                    print(f"Nota {folio_recuperar} no ha sido recuperada.")
                return
        
        print("El folio de la nota no existe o no corresponde a una nota cancelada.")
    
    except Exception as e:
        print(f"Error al recuperar una nota: {str(e)}")

# Función para consultar notas por período
def consultar_notas_por_periodo(cursor):
    while True:
        try:
            fecha_inicial = input("Ingrese la fecha inicial del período (en formato DD-MM-YYYY) o presione Enter para utilizar '01-01-2000': ")
            if not fecha_inicial:
                fecha_inicial = datetime.datetime(2000, 1, 1).date()  # Fecha por defecto: 01-01-2000
                print("Fecha inicial asume el valor de 01-01-2000.")
            else:
                fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d-%m-%Y").date()
                if fecha_inicial > datetime.date.today():
                    print("\n*****ERROR: La fecha inicial no debe ser posterior a la fecha actual.*****")
                    continue
            break
        except ValueError:
            print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")

    while True:
        try:
            fecha_final = input("Ingrese la fecha final del período (en formato DD-MM-YYYY) o presione Enter para utilizar la fecha actual: ")
            if not fecha_final:
                fecha_final = datetime.datetime.now().date()
                print(f"La fecha final asume el valor de {fecha_final.strftime('%d-%m-%Y')}")
            else:
                fecha_final = datetime.datetime.strptime(fecha_final, "%d-%m-%Y").date()
                if fecha_final <= fecha_inicial:
                    print("\n*****ERROR: La fecha final debe ser posterior o igual a la fecha inicial.*****")
                    continue
            break
        except ValueError:
            print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")

    while True:
        cursor.execute("SELECT Folio, Fecha, Clave_Cliente, Monto FROM Notas WHERE Fecha >= ? AND Fecha <= ?", (fecha_inicial, fecha_final.strftime("%d-%m-%Y")))
        notas = cursor.fetchall()

        if notas:
            monto_promedio = sum(nota[3] for nota in notas) / len(notas)
            print("Notas registradas en el período:")
            for nota in notas:
                print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Clave de Cliente: {nota[2]}, Monto: {nota[3]}")

            print(f"Monto promedio de las notas en el período: {monto_promedio}")

            opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (CSV/Excel/Regresar): ").lower()

            if "csv" in opcion:
                fecha_inicial_str = fecha_inicial.strftime("%m-%d-%Y")
                fecha_final_str = fecha_final.strftime("%m-%d-%Y")

                nombre_archivo = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.csv"
                df = pd.DataFrame(notas, columns=["Folio", "Fecha", "Clave_Cliente", "Monto"])
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif "excel" in opcion:
                fecha_inicial_str = fecha_inicial.strftime("%m-%d-%Y")
                fecha_final_str = fecha_final.strftime("%m-%d-%Y")

                nombre_archivo = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.xlsx"
                df = pd.DataFrame(notas, columns=["Folio", "Fecha", "Clave_Cliente", "Monto"])
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif "regresar" in opcion:
                break
            else:
                print("Opción no válida. Por favor, seleccione 'CSV', 'Excel' o 'Regresar'.")
        else:
            print("No hay notas registradas en el período especificado.")
            opcion = input("¿Desea regresar al menú de reportes? (Sí/No): ").lower()
            if opcion == "si":
                break

# Función para consultar nota por folio
def consultar_nota_por_folio(cursor):
    try:
        folio_consultar = input("Ingrese el folio de la nota a consultar: ")
        
        if not folio_consultar.isdigit():
            print("Folio de nota no válido.")
            return
        
        folio_consultar = int(folio_consultar)
#       cursor.execute("SELECT n.Folio, n.Fecha, n.Clave_Cliente, n.Monto, c.Nombre_Cliente, c.RFC, c.Correo, s.Nombre_Servicio, s.Costo FROM Notas n JOIN Clientes c ON n.Clave_Cliente = c.Clave_Cliente JOIN Detalles_Nota dn ON n.Folio = dn.Clave_Nota JOIN Servicios s ON dn.Clave_Servicio = s.Clave_Servicio WHERE n.Folio = ? AND n.Cancelada = 0", (folio_consultar,))   
        cursor.execute("SELECT n.Folio, n.Fecha, n.Clave_Cliente, n.Monto, c.Nombre_Cliente, c.RFC, c.Correo, s.Nombre_Servicio, s.Costo FROM Notas n JOIN Clientes c ON n.Clave_Cliente = c.Clave_Cliente JOIN Detalles_Nota dn ON n.Folio = dn.Folio JOIN Servicios s ON dn.Clave_Servicio = s.Clave_Servicio WHERE n.Folio = ? AND n.Cancelada = 0", (folio_consultar,))

        nota = cursor.fetchone()
        
        if nota:
            print("Detalle de la nota:")
            print(f"Folio: {nota[0]}")
            print(f"Fecha: {nota[1]}")
            print(f"Clave de Cliente: {nota[2]}")
            print(f"Nombre del Cliente: {nota[4]}")
            print(f"RFC del Cliente: {nota[5]}")
            print(f"Correo del Cliente: {nota[6]}")
            print(f"Monto: {nota[3]}")
            print(f"Servicio: {nota[7]}")
            print(f"Costo del Servicio: {nota[8]}")
        else:
            print("La nota no existe o está cancelada.")
    
    except Exception as e:
        print(f"Error al consultar una nota por folio: {str(e)}")

# Función para el menú de notas
def menu_notas(cursor):
    while True:
        print("\nMenú Notas:")
        print("1. Registrar una nota")
        print("2. Cancelar una nota")
        print("3. Recuperar una nota")
        print("4. Consultas y reportes de notas")
        print("5. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_nota(cursor)
        elif opcion == "2":
            cancelar_nota(cursor)
        elif opcion == "3":
            recuperar_nota(cursor)
        elif opcion == "4":
            while True:
                print("\nConsultas y reportes de notas:")
                print("1. Consulta por período")
                print("2. Consulta por folio")
                print("3. Volver al menú anterior")

                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    consultar_notas_por_periodo(cursor)
                elif reporte_opcion == "2":
                    consultar_nota_por_folio(cursor)
                elif reporte_opcion == "3":
                    break
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "5":
            print("Redirigiendo al menú principal")
            return

# Función para agregar un cliente.
def agregar_cliente(cursor):
    nombre_cliente = None
    rfc_cliente = None
    correo_cliente = None

    while nombre_cliente is None:
        nombre_cliente = input("Ingrese el nombre del cliente: ")
        if not nombre_cliente.strip():
            print("El nombre del cliente no puede estar vacío. Inténtelo de nuevo.")
            nombre_cliente = None

    while rfc_cliente is None:
        rfc_cliente = input("Ingrese el RFC del cliente: ")
        if not validar_rfc_persona_fisica(rfc_cliente):
            print("El RFC ingresado no es válido. Inténtelo de nuevo.")
            rfc_cliente = None

    while correo_cliente is None:
        correo_cliente = input("Ingrese el correo electrónico del cliente: ")
        if not validar_correo(correo_cliente):
            print("El correo electrónico ingresado no es válido. Inténtelo de nuevo.")
            correo_cliente = None

    try:
        cursor.execute("INSERT INTO Clientes (Nombre_Cliente, RFC, Correo) VALUES (?, ?, ?)",
                       (nombre_cliente, rfc_cliente, correo_cliente))
        print("Cliente registrado con éxito.")
    except Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')

# Función para listar clientes ordenados por clave
def listar_clientes_por_clave(cursor):
    cursor.execute("SELECT Clave_Cliente, Nombre_Cliente, RFC, Correo FROM Clientes ORDER BY Clave_Cliente")
    clientes = cursor.fetchall()
    
    if not clientes:
        print("No hay clientes registrados. Registre un cliente antes de crear una lista.")
        return
     
    # DataFrame
    df = pd.DataFrame(clientes, columns=["Clave_Cliente", "Nombre_Cliente", "RFC", "Correo"])
    
    # Ordenar el DataFrame por la columna 'Clave_Cliente'
    df = df.sort_values(by='Clave_Cliente')
    
    print("Listado de clientes registrados ordenados por clave:")   
    print(df)
    
    # Exportar resultados.
    while True:
        opcion_exportacion = input("¿Desea exportar el reporte a CSV, Excel o regresar al menú de reportes? ").lower()

        # Damos formato a la fecha
        fecha_actual = datetime.now().strftime("%m_%d_%Y")

        # Crear el nombre del archivo según el patrón
        nombre_archivo = f"ReporteClientesActivosPorClave_{fecha_actual}.{opcion_exportacion}"

        # Exportar los datos a CSV.
        if opcion_exportacion == "csv":
            df.to_csv(nombre_archivo, index=False)
            print(f"Los datos se han exportado a {opcion_exportacion} con el nombre: {nombre_archivo}")
            break
        elif opcion_exportacion == "excel":
            # Exportar a Excel utilizando pandas
            df.to_excel(nombre_archivo, index=False)
            print(f"Los datos se han exportado a {opcion_exportacion} con el nombre: {nombre_archivo}")
            break
        elif opcion_exportacion == "regresar":
            print("Redirigiendo al menú de reportes")
            return
        else:
            print("Opción no válida. Por favor, elija entre CSV, Excel o regresar al menú de reportes.")

# Función para listar clientes ordenados por nombre
def listar_clientes_por_nombre(cursor):
    cursor.execute("SELECT Clave_Cliente, Nombre_Cliente, RFC, Correo FROM Clientes ORDER BY Nombre_Cliente")
    clientes = cursor.fetchall()

    if not clientes:
        print("No hay clientes registrados. Registre un cliente antes de crear una lista.")
        return
    
    # DataFrame
    df = pd.DataFrame(clientes, columns=["Clave_Cliente", "Nombre_Cliente", "RFC", "Correo"])
    
    # Ordenar el DataFrame por la columna 'Nombre_Cliente'
    df = df.sort_values(by='Nombre_Cliente')
    
    print("Listado de clientes registrados ordenados por nombre:")   
    print(df)
    
    # Exportar resultados.
    while True:
        opcion_exportacion = input("¿Desea exportar el reporte a CSV, Excel o regresar al menú de reportes? ").lower()
        if opcion_exportacion in ["csv", "excel", "regresar"]:
            break
        else:
            print("Opción no válida. Por favor, elija entre CSV, Excel o regresar al menú de reportes.")

    if opcion_exportacion == "regresar":
        print("Redirigiendo al menú de reportes")
        return  

    # Obtener la fecha actual en el formato mm_dd_aaaa
    fecha_actual = datetime.now().strftime("%m_%d_%Y")

    # Crear el nombre del archivo según el patrón
    nombre_archivo = f"ReporteClientesActivosPorNombre_{fecha_actual}.{opcion_exportacion}"

    # Exportar a csv.
    if opcion_exportacion == "csv":
        df.to_csv(nombre_archivo, index=False)
        print(f"Los datos se han exportado a {opcion_exportacion} con el nombre: {nombre_archivo}")
    elif opcion_exportacion == "excel":
        # Exportar a Excel. 
        df.to_excel(nombre_archivo, index=False)
        print(f"Los datos se han exportado a {opcion_exportacion} con el nombre: {nombre_archivo}")
        
# Función para el menú de clientes
def menu_clientes(cursor):
    while True:
        print("\nMenú Clientes:")
        print("1. Agregar un cliente")
        print("2. Consultas y reportes de clientes")
        print("3. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_cliente(cursor)
        elif opcion == "2":
            while True:
                print("\nConsultas y reportes de clientes:")
                print("1. Listado de clientes registrados ordenados por clave")
                print("2. Listado de clientes registrados ordenados por nombre")
                print("3. Volver al menú anterior")

                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    listar_clientes_por_clave(cursor)
                elif reporte_opcion == "2":
                    listar_clientes_por_nombre(cursor)
                elif reporte_opcion == "3":
                    confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de clientes? (S. Si / N. No): ")
                    while confirmacion_salir.upper() not in ('S', 'N'):
                        print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                        confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de clientes? (S/N): ")

                    if confirmacion_salir.upper() == 'S':
                        print("\nSaliendo de Consultas y reportes de clientes...")
                        break  # Salir del ciclo while
                    elif confirmacion_salir.upper() == 'N':
                        print("\nVolviendo al menú anterior...")
                        continue
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "3":
            confirmacion_salir = input("¿Está seguro que desea salir del Menú Clientes? (S. Si / N. No): ")
            while confirmacion_salir.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion_salir = input("¿Está seguro que desea salir del Menú Clientes? (S/N): ")

            if confirmacion_salir.upper() == 'S':
                print("Redirigiendo al menú principal...")
                break
            elif confirmacion_salir.upper() == 'N':
                print("\nVolviendo al menú anterior...")
                continue
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

# Función para validar el formato de RFC persona física.
def validar_rfc_persona_fisica(rfc):
    rfc_patron_fisica = r'^[A-Z]{4}\d{6}[A-Z\d]{3}$'
    return bool(re.match(rfc_patron_fisica, rfc))

# Función para validar el formato de correo electrónico.
def validar_correo(correo):
    correo_patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(correo_patron, correo))

# Función para agregar un servicio
def agregar_servicio(cursor):
    try:
        nombre_servicio = input("Ingrese el nombre del servicio: ")
        costo_servicio = float(input("Ingrese el costo del servicio: "))

        if nombre_servicio.strip() and costo_servicio > 0:
            cursor.execute("INSERT INTO Servicios (Nombre_Servicio, Costo) VALUES (?, ?)",
                           (nombre_servicio, costo_servicio))
            print("Servicio registrado con éxito.")
        else:
            print("Datos de servicio no válidos. Verifique el nombre y el costo.")
    except Exception as e:
        print(f"Error al agregar un servicio: {str(e)}")

# Función para buscar servicio por clave
def buscar_servicio_por_clave(cursor):
    cursor.execute("SELECT Clave_Servicio, Nombre_Servicio FROM Servicios")
    servicios = cursor.fetchall()
    
    if not servicios:
        print("No hay servicios registrados. Registre un servicio antes de crear una lista.")
        return
        
    if servicios:
        print("Listado de servicios registrados (clave - nombre):")
        for servicio in servicios:
            print(f"{servicio[0]} - {servicio[1]}")

        clave_servicio = input("Seleccione la clave de servicio para ver detalles: ")
        cursor.execute("SELECT Nombre_Servicio, Costo FROM Servicios WHERE Clave_Servicio = ?", (clave_servicio,))
        servicio = cursor.fetchone()

        if servicio:
            print(f"Detalles del servicio (clave {clave_servicio}):")
            print(f"Nombre: {servicio[0]}")
            print(f"Costo: {servicio[1]}")
        else:
            print("Clave de servicio no encontrada.")
    #else:
        #print("No hay servicios registrados.")

# Función para buscar servicio por nombre
def buscar_servicio_por_nombre(cursor):
    nombre_servicio = input("Ingrese el nombre del servicio a buscar: ")
    cursor.execute("SELECT Nombre_Servicio, Costo FROM Servicios WHERE UPPER(Nombre_Servicio) = UPPER(?)", (nombre_servicio,))
    servicio = cursor.fetchone()

    #if not servicio:
        #print("No hay servicios registrados. Registre un servicio antes de crear una lista.")
        #return
    
    if servicio:
        print(f"Detalles del servicio (nombre '{nombre_servicio}'):")
        print(f"Nombre: {servicio[0]}")
        print(f"Costo: {servicio[1]}")
    else:
        print("Servicio no encontrado.")

# Función para listar servicios ordenados por clave
def listar_servicios_por_clave(cursor):
    cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios ORDER BY Clave_Servicio")
    servicios = cursor.fetchall()
    
    if not servicios:
        print("No se han encontrado servicios.")
        return
    
    # Crear un DataFrame con los datos
    df = pd.DataFrame(servicios, columns=["Clave_Servicio", "Nombre_Servicio", "Costo"])
    
    # Ordenar el DataFrame por la columna 'Clave_Servicio'
    df = df.sort_values(by='Clave_Servicio')
    
    print("Listado de servicios registrados ordenados por clave:")
    print(df)  


    while True:
        exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (CSV/Excel/Regresar): ").lower()
        if exportar_opcion == "csv":
            fecha_actual = obtener_fecha_actual()
            nombre_archivo = f"ReporteServiciosPorClave_{fecha_actual}.csv"
            df.to_csv(nombre_archivo, index=False)
            print(f"El reporte ha sido exportado a '{nombre_archivo}'")
        elif exportar_opcion == "excel":
            fecha_actual = obtener_fecha_actual()
            nombre_archivo = f"ReporteServiciosPorClave_{fecha_actual}.xlsx"
            df.to_excel(nombre_archivo, index=False)
            print(f"El reporte ha sido exportado a '{nombre_archivo}'")
        elif exportar_opcion == "regresar":
            return
        else:
            print("Opción no válida. Por favor, elija entre CSV, Excel o regresar al menú de reportes.")

# Función para listar servicios ordenados por nombre
def listar_servicios_por_nombre(cursor):
    cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios ORDER BY Nombre_Servicio")
    servicios = cursor.fetchall()

    if not servicios:
        print("No se han encontrado servicios.")
        
    # Crear un DataFrame con los datos
    df = pd.DataFrame(servicios, columns=["Clave_Servicio", "Nombre_Servicio", "Costo"])
    
    # Ordenar el DataFrame por la columna 'Nombre_Servicio'
    df = df.sort_values(by='Nombre_Servicio')
    
    print("Listado de servicios registrados ordenados por nombre:")
    print(df)  

    while True:
        exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (CSV/Excel/Regresar): ").lower()
        if exportar_opcion == "csv":
            fecha_actual = obtener_fecha_actual()
            nombre_archivo = f"ReporteServiciosPorNombre_{fecha_actual}.csv"
            df.to_csv(nombre_archivo, index=False)
            print(f"El reporte ha sido exportado a '{nombre_archivo}'")
        elif exportar_opcion == "excel":
            fecha_actual = obtener_fecha_actual()
            nombre_archivo = f"ReporteServiciosPorNombre_{fecha_actual}.xlsx"
            df.to_excel(nombre_archivo, index=False)
            print(f"El reporte ha sido exportado a '{nombre_archivo}'")
        elif exportar_opcion == "regresar":
            return
        else:
            print("Opción no válida. Por favor, elija entre CSV, Excel o regresar al menú de reportes.")


# Función para el menú de servicios
def menu_servicios(cursor):
    while True:
        print("\nMenú Servicios:")
        print("1. Agregar un servicio")
        print("2. Consultas y reportes de servicios")
        print("3. Listado de servicios")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_servicio(cursor)
            
        elif opcion == "2":
            while True:
                print("\nConsultas y reportes de servicios:")
                print("1. Búsqueda por clave de servicio")
                print("2. Búsqueda por nombre de servicio")
                print("3. Volver al menú anterior")
                
                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    buscar_servicio_por_clave(cursor)
                elif reporte_opcion == "2":
                    buscar_servicio_por_nombre(cursor)
                elif reporte_opcion == "3":
                    confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de servicios? (S. Si / N. No): ")
                    while confirmacion_salir.upper() not in ('S', 'N'):
                        print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                        confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de servicios? (S/N): ")

                    if confirmacion_salir.upper() == 'S':
                        print("\nSaliendo de Consultas y reportes de servicios...")
                        break  # Salir del ciclo while
                    elif confirmacion_salir.upper() == 'N':
                        print("\nVolviendo al menú anterior...")
                        continue
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
                    
        elif opcion == "3":
            while True:
                print("\nListado de servicios:")
                print("1. Listado de servicios ordenados por clave")
                print("2. Listado de servicios ordenados por nombre de servicio")
                print("3. Volver al menú anterior")
                
                listado_opcion = input("Seleccione una opción: ")

                if listado_opcion == "1":
                    listar_servicios_por_clave(cursor)
                elif listado_opcion == "2":
                    listar_servicios_por_nombre(cursor)
                elif listado_opcion == "3":
                    confirmacion_salir = input("¿Está seguro que desea salir de Listado de servicios? (S. Si / N. No): ")
                    while confirmacion_salir.upper() not in ('S', 'N'):
                        print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                        confirmacion_salir = input("¿Está seguro que desea salir de Listado de servicios? (S/N): ")

                    if confirmacion_salir.upper() == 'S':
                        print("\nSaliendo de Listado de servicios...")
                        break  # Salir del ciclo while
                    elif confirmacion_salir.upper() == 'N':
                        print("\nVolviendo al menú anterior...")
                        continue
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
                    
        elif opcion == "4":
            confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
            while confirmacion_salir.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion_salir = input("¿Está seguro que desea salir? (S/N): ")

            if confirmacion_salir.upper() == 'S':
                print("\nSaliendo del programa...")
                break  # Salir del ciclo while

            elif confirmacion_salir.upper() == 'N':
                print("\nRedirigiendo al menú principal...")
                continue
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
  
# Función para el menú principal
def main():
    # Conexión a la base de datos
    try:
        conexion = sqlite3.connect("Evidencia_3_SEMB_1799759.db")
        cursor = conexion.cursor()
        
        # Crear las tablas en la base de datos
        crear_tablas(cursor)
        
        while True:
            print("\nMenú Principal - Taller Mecánico Morales:")
            print("1. Menú Notas.")
            print("2. Menú Clientes")
            print("3. Menú Servicios")
            print("4. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                menu_notas(cursor)
            elif opcion == "2":
                menu_clientes(cursor)
            elif opcion == "3":
                menu_servicios(cursor)
            elif opcion == "4":
                confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
                while confirmacion_salir.upper() not in ('S', 'N'):
                    print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                    confirmacion_salir = input("¿Está seguro que desea salir? (S/N): ")

                if confirmacion_salir.upper() == 'S':
                    print("\nSaliendo del programa...")
                    break  # Salir del ciclo while

                elif confirmacion_salir.upper() == 'N':
                    print("\nRedirigiendo al menú principal...")
                    continue

            else:
                print("\nOpción no válida. Por favor, seleccione una opción válida.")
    
    except Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    finally:
        if conexion:
            conexion.close()

if __name__ == "__main__":
    main()


