import sqlite3
import re
import csv
import datetime
from sqlite3 import Error
import sys
import pandas as pd

def crear_tablas():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Clientes (Clave_Cliente INTEGER PRIMARY KEY NOT NULL, Nombre_Cliente TEXT NOT NULL, RFC TEXT NOT NULL, Correo TEXT NOT NULL, Suspendido INTEGER DEFAULT 0)")
        cursor.execute("CREATE TABLE IF NOT EXISTS Servicios (Clave_Servicio INTEGER PRIMARY KEY NOT NULL, Nombre_Servicio TEXT NOT NULL, Costo REAL NOT NULL, Suspendido INTEGER DEFAULT 0)")
        cursor.execute("CREATE TABLE IF NOT EXISTS Notas (Folio INTEGER PRIMARY KEY NOT NULL, Fecha DATE timestamp NOT NULL, Clave_Cliente INTEGER NOT NULL, Monto REAL NOT NULL, Cancelada INTEGER DEFAULT 0, FOREIGN KEY (Clave_Cliente) REFERENCES Clientes(Clave_Cliente))")
        cursor.execute("CREATE TABLE IF NOT EXISTS Detalles_Nota (Clave_Detalle INTEGER PRIMARY KEY NOT NULL, Folio INTEGER, Clave_Servicio INTEGER, FOREIGN KEY (Folio) REFERENCES Notas(Folio), FOREIGN KEY (Clave_Servicio) REFERENCES Servicios(Clave_Servicio))")
        conexion.commit()
        print("Tablas creadas exitosamente.")
        
    except sqlite3.Error as e:
        print(f"Error al crear tablas en la base de datos: {e}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def obtener_fecha_actual():
    fecha_actual = datetime.date.today()
    return fecha_actual

def validar_rfc_persona_fisica(rfc):
    rfc_patron_fisica = r'^[A-Z]{4}\d{6}[A-Z\d]{3}$'
    return bool(re.match(rfc_patron_fisica, rfc))

def validar_correo(correo):
    correo_patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(correo_patron, correo))

def registrar_nota():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()        
        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente FROM Clientes")
        clientes = cursor.fetchall()
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios")
        servicios = cursor.fetchall()
              
        if not clientes:
            print("No hay clientes registrados. Registre un cliente antes de crear una nota.")
            return
        
        if not servicios:
            print("No hay servicios registrados. Registre un servicio antes de crear una nota.")
            return
        
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}.')        
    finally:
        if conexion:
            conexion.close()

    print("Ingrese la fecha de la realización de la nota (DD-MM-AAAA).")
    while True:
        fecha_registro = input("Fecha: ").strip()
        try:
            fecha_procesada = datetime.datetime.strptime(fecha_registro, "%d-%m-%Y").date()

            if fecha_procesada > datetime.date.today():
                print("\nLa fecha ingresada no debe ser posterior a la fecha actual.\nIngrese una fecha válida.")
                continue
            break
        except ValueError:
            print("\nIngrese una fecha válida en formato (DD-MM-AAAA).")        
    
    print("Clientes registrados. NO SUSPENDIDOS:")
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()           
        cursor.execute("SELECT * FROM Clientes WHERE Suspendido = 0")
        clientes = cursor.fetchall()

        df = pd.DataFrame(clientes, columns=["Clave_Cliente", "Nombre_Cliente", "RFC", "Correo", "Estado"])
        
        df = df.sort_values(by='Clave_Cliente')

        df = df.set_index('Clave_Cliente')
        
        print(df)
        
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
        
    clave_cliente = None 

    while True:
        while True:
            clave_cliente_input = input("Ingrese la clave del cliente: ").strip()
            if clave_cliente_input.isdigit():
                clave_cliente = int(clave_cliente_input)
                break  
            else:
                print("\nIngrese un número válido.")
        try:
            conexion = sqlite3.connect("PIA_SEMB_1799759.db")
            cursor = conexion.cursor() 
            cursor.execute("SELECT COUNT(*) FROM Clientes WHERE Clave_Cliente = ? AND Suspendido = 0", (clave_cliente,))
            if cursor.fetchone()[0] > 0:
                break
            else:
                print("\nEl cliente con la clave proporcionada no existe o se encuentra suspendido, ingrese una clave válida.")
        
        except Error as e:
            print(e)
        except Exception:
            print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
        finally:
            if conexion:
                conexion.close()
                
    servicios_seleccionados = []
    cantidadServicios = 0
    costos_servicios = []
    
    print("Servicios registrados. NO SUSPENDIDOS:")
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()          
        cursor.execute("SELECT * FROM Servicios WHERE Suspendido = 0")
        servicios = cursor.fetchall()

        df = pd.DataFrame(servicios, columns=["Clave_Servicio", "Nombre_Servicio", "Costo", "Estado"])
        
        df = df.sort_values(by='Clave_Servicio')

        df = df.set_index('Clave_Servicio')
        
        print(df)
        
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

    while True:
        clave_servicio = None  
        cantidad_servicios = 0
        try:
            conexion = sqlite3.connect("PIA_SEMB_1799759.db")
            cursor = conexion.cursor()

            clave_servicio_input = input("Ingrese la clave del servicio: ").strip()
            if clave_servicio_input.isdigit():
                clave_servicio = int(clave_servicio_input)
            else:
                print("Ingrese un número válido.")
                continue
            
            cursor.execute("SELECT COUNT(*) FROM Servicios WHERE Clave_Servicio = ? AND Suspendido = 0", (clave_servicio,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("SELECT Costo FROM Servicios WHERE Clave_Servicio = ? AND Suspendido = 0", (clave_servicio,))
                servicios_seleccionados.append(clave_servicio)
                costo_servicio = cursor.fetchone()[0]
                costos_servicios.append(costo_servicio)
                cantidad_servicios += 1

                otro_servicio = input('\t¿Quiere agregar otro servicio? (S. Si / N. No): ').upper()
                if otro_servicio == 'S':
                    continue
                elif otro_servicio == 'N':
                    break
                else:
                    print("Seleccione S. Para agregar otro servicio. N. Para generar la nota.")
            else:
                print("El servicio no existe o se encuentra suspendido.")
        except Error as e:
            print(e)
        except Exception:
            print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
        finally:
            if conexion:
                conexion.close()

    monto_a_pagar = sum(costos_servicios)

    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()          
        datos_notas = (fecha_procesada, clave_cliente, monto_a_pagar)
        cursor.execute("INSERT INTO Notas(Fecha, Clave_Cliente, Monto) \
                            VALUES (?, ?, ?)", datos_notas)
        folio = cursor.lastrowid
        conexion.commit()
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        for clave_servicio in servicios_seleccionados:
            cursor.execute("INSERT INTO Detalles_Nota(Folio, Clave_Servicio) VALUES (?, ?)",(folio, clave_servicio))
            #Clave_Detalle = cursor.lastrowid
            conexion.commit()
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close() 
    print("Nota guardada correctamente.")
    
    try:
            conexion = sqlite3.connect("PIA_SEMB_1799759.db")
            cursor = conexion.cursor()          
            cursor.execute("""
                SELECT 
                    N.Folio, 
                    N.Fecha, 
                    C.Nombre_Cliente AS 'Cliente', 
                    C.RFC, 
                    C.Correo AS 'Correo Electrónico', 
                    N.Monto AS 'Total'
                FROM Notas N
                INNER JOIN Clientes C ON N.Clave_Cliente = C.Clave_Cliente
                WHERE N.Folio = ?;
            """, (folio,))
            nota_generada = cursor.fetchall()

            if nota_generada:
                print("Datos de la nota guardada:")
                df = pd.DataFrame(nota_generada, columns=["Folio", "Fecha", "Cliente", "RFC", "Correo Elecrónico", "Total"])
                print(df)  
            else:
                print("No se encontró la nota guardada.")
    except sqlite3.Error as e:
        print(e)
    finally:
        if conexion:
            conexion.close()

    try:
            conexion = sqlite3.connect("PIA_SEMB_1799759.db")
            cursor = conexion.cursor()        
            cursor.execute("""
                SELECT 
                    S.Nombre_Servicio AS 'Servicio', 
                    S.Costo AS 'Precio'
                FROM Detalles_Nota DN
                INNER JOIN Servicios S ON DN.Clave_Servicio = S.Clave_Servicio
                WHERE DN.Folio = ?;
            """, (folio,))
            detalle_nota = cursor.fetchall()

            if detalle_nota:
                print("\nDetalle de la nota generada:")
                df = pd.DataFrame(detalle_nota, columns=["Servicio", "Precio"])
                print(df)
            else:
                print("No se encontraron los detalles de la nota guardada.")
    except Error as e:
        print(e)
    finally:
        if conexion:
            conexion.close()

def cancelar_nota():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM Notas WHERE Cancelada = 0")
        notas_activas = cursor.fetchall()  

        if not notas_activas:
            print("No se encontraron notas activas.")
            return
        
        print("Notas activas")
        for nota in notas_activas:
            print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Clave_Cliente: {nota[2]}, Monto: {nota[3]}")

        clave_seleccionada = input("Ingrese el folio de la nota a cancelar: ")

        if not clave_seleccionada.isdigit():
            print("Folio no válido.")
            return

        clave_seleccionada = int(clave_seleccionada)

        clave_valida = False
        for nota in notas_activas:
            if clave_seleccionada == nota[0]:
                clave_valida = True
                break

        if not clave_valida:
            print("Clave de servicio no válida.")
            return

        cursor.execute("SELECT * FROM Notas WHERE Folio = ? AND Cancelada = 0", (clave_seleccionada,))
        nota = cursor.fetchone()

        if nota is None:
            print("La nota ya está cancelada.")
            return

        print("Datos de la nota a cancelar:")
        print(f"Folio: {nota[0]}")
        print(f"Fecha: {nota[1]}")
        print(f"Clave: {nota[2]}")
        print(f"Monto: {nota[3]}")
        print(f"Estado: {nota[4]}")

        confirmacion = input("¿Desea cancelar esta nota? (S. Sí/ N. No): ")

        if confirmacion.upper() == "S":
            cursor.execute("UPDATE Notas SET Cancelada = 1 WHERE Folio = ?", (clave_seleccionada,))
            conexion.commit()
            print(f"Nota {clave_seleccionada} cancelada con éxito.")
        else:
            print("Operación cancelada.")

    except sqlite3.Error as e:
        print(f"Error al cancelar la nota: {e}")
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def recuperar_nota():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        
        cursor.execute("SELECT * FROM Notas WHERE Cancelada = 1")
        notas_canceladas = cursor.fetchall()  # Usar fetchall para obtener todas las filas

        if not notas_canceladas:
            print("No se encontraron notas canceladas.")
            return

        print("Notas canceladas")
        for nota in notas_canceladas:
            print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Clave_Cliente: {nota[2]}, Monto: {nota[3]}, Estado: {nota[4]}")

        clave_seleccionada = input("Ingrese el folio de la nota a recuperar: ")

        if not clave_seleccionada.isdigit():
            print("Folio de nota no válido.")
            return
        
        clave_seleccionada = int(clave_seleccionada)

        clave_valida = False
        for nota in notas_canceladas:
            if clave_seleccionada == nota[0]:
                clave_valida = True
                break

        if not clave_valida:
            print("Folio de nota no válido.")
            return

        cursor.execute("SELECT * FROM Notas WHERE Folio = ? AND Cancelada = 1", (clave_seleccionada,))
        nota = cursor.fetchone()
        
        if nota is None:
            print("La nota no está cancelada.")
            return
        
        print("Datos de la nota a recuperar:")
        print(f"Folio: {nota[0]}")
        print(f"Fecha: {nota[1]}")
        print(f"Clave: {nota[2]}")
        print(f"Monto: {nota[3]}")
        print(f"Estado: {nota[4]}")

        confirmacion = input("¿Desea recuperar esta nota? (S. Sí/ N. No): ")
        
        if confirmacion.upper() == "S":
            cursor.execute("UPDATE Notas SET Cancelada = 0 WHERE Folio = ?", (clave_seleccionada,))
            conexion.commit()
            print(f"Nota {clave_seleccionada} recuperada con éxito.")
        else:
            print("Operación cancelada.")
        
    except sqlite3.Error as e:
        print(f"Error al recuperar la nota: {e}")
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def consultar_notas_por_periodo():
    while True:
        try:
            fecha_inicial = input("Ingrese la fecha inicial del período (en formato DD-MM-YYYY) o presione Enter para utilizar '01-01-2000': ")
            if not fecha_inicial:
                fecha_inicial = datetime.datetime(2000, 1, 1).date()  
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
        try:
            conexion = sqlite3.connect("PIA_SEMB_1799759.db")
            cursor = conexion.cursor()              
            cursor.execute("SELECT Folio, strftime('%d-%m-%Y', Fecha), Clave_Cliente, Monto FROM Notas WHERE (Fecha BETWEEN ? AND ?) AND Cancelada = 0", (fecha_inicial, fecha_final))
            notas = cursor.fetchall()

            if notas:
                monto_promedio = sum(nota[3] for nota in notas) / len(notas)
                print("Notas registradas en el período:")
                for nota in notas:
                    print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Clave de Cliente: {nota[2]}, Monto: {nota[3]}")

                print(f"Monto promedio de las notas en el período: {monto_promedio}")

                opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (1. CSV/ 2. Excel/ 3. Regresar): ").lower()

                if "1" in opcion:
                    fecha_inicial_str = fecha_inicial.strftime("%m-%d-%Y")
                    fecha_final_str = fecha_final.strftime("%m-%d-%Y")

                    nombre_archivo = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.csv"
                    df = pd.DataFrame(notas, columns=["Folio", "Fecha", "Clave_Cliente", "Monto"])
                    df.to_csv(nombre_archivo, index=False)
                    print(f"El reporte ha sido exportado a '{nombre_archivo}'")
                elif "2" in opcion:
                    fecha_inicial_str = fecha_inicial.strftime("%m-%d-%Y")
                    fecha_final_str = fecha_final.strftime("%m-%d-%Y")

                    nombre_archivo = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.xlsx"
                    df = pd.DataFrame(notas, columns=["Folio", "Fecha", "Clave_Cliente", "Monto"])
                    df.to_excel(nombre_archivo, index=False)
                    print(f"El reporte ha sido exportado a '{nombre_archivo}'")
                elif "3" in opcion:
                    print("Redirigiendo al menú de reportes... ")
                    break
                else:
                    print("Opción no válida. Por favor, seleccione 'CSV', 'Excel' o 'Regresar'.")
            else:
                print("No hay notas registradas en el período especificado.")
                opcion = input("¿Desea regresar al menú de reportes? (S. Sí/ N. No): ").upper()
                if opcion == "S":
                    print("Redirigiendo al menú de reportes... ")
                    break
        except Error as e:
            print(e)      
        except Exception as ex:
            print(f"Error al recuperar una nota: {str(ex)}")
        finally:
            if conexion:
                conexion.close()

def consultar_nota_por_folio():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()           
        folio_consultar = input("Ingrese el folio de la nota a consultar: ")
        
        if not folio_consultar.isdigit():
            print("Folio de nota no válido.")
            return
        
        folio_consultar = int(folio_consultar)
        
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
    except Error as e:
        print(e)     
    except Exception as e:
        print(f"Error al consultar una nota por folio: {str(e)}")
    finally:
        if conexion:
            conexion.close()
            
def menu_notas():
    while True:
        print("\nMenú Notas:")
        print("1. Registrar una nota")
        print("2. Cancelar una nota")
        print("3. Recuperar una nota")
        print("4. Consultas y reportes de notas")
        print("5. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_nota()
        elif opcion == "2":
            cancelar_nota()
        elif opcion == "3":
            recuperar_nota()
        elif opcion == "4":
            while True:
                print("\nConsultas y reportes de notas:")
                print("1. Consulta por período")
                print("2. Consulta por folio")
                print("3. Volver al menú anterior")

                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    consultar_notas_por_periodo()
                elif reporte_opcion == "2":
                    consultar_nota_por_folio()
                elif reporte_opcion == "3":
                    print("Redirigiendo al menú de notas... ")
                    break
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "5":
            print("Redirigiendo al menú principal")
            return
        else:
            print("Opción no valida. Seleccione una opción valida")
        
def agregar_cliente():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()        
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

        cursor.execute("INSERT INTO Clientes (Nombre_Cliente, RFC, Correo) VALUES (?, ?, ?)",
                       (nombre_cliente, rfc_cliente, correo_cliente))
        conexion.commit()
        print("Cliente registrado con éxito.")
    except Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def suspender_cliente():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente FROM Clientes WHERE Suspendido = 0")
        clientes_activos = cursor.fetchall()

        if not clientes_activos:
            print("No hay clientes activos para suspender.")
            return

        print("Clientes activos:")
        for clave, nombre in clientes_activos:
            print(f"{clave}: {nombre}")

        clave_cliente = input("Ingrese la clave del cliente que desea suspender (0 para volver al menú anterior):")
        
        if clave_cliente == '0':
            print("Redirigiendo al menú de clientes... ")
            return

        if not clave_cliente.isdigit():
            print("Clave de cliente no válida.")
            return

        clave_cliente = int(clave_cliente)

        cliente_valido = False
        for clave, _ in clientes_activos:
            if clave_cliente == clave:
                cliente_valido = True
                break

        if cliente_valido:
            cursor.execute("SELECT Nombre_Cliente, RFC, Correo FROM Clientes WHERE Clave_Cliente = ?", (clave_cliente,))
            nombre_cliente, rfc_cliente, correo_cliente = cursor.fetchone()

            print(f"Datos del cliente a suspender:")
            print(f"Nombre: {nombre_cliente}")
            print(f"RFC: {rfc_cliente}")
            print(f"Correo: {correo_cliente}")

            confirmacion = input("¿Desea suspender a este cliente? (S/N): ")

            if confirmacion.upper() == 'S':
                # Suspender al cliente.
                cursor.execute("UPDATE Clientes SET Suspendido = 1 WHERE Clave_Cliente = ?", (clave_cliente,))
                conexion.commit()
                print("Cliente suspendido con éxito.")
            else:
                print("Operación cancelada.")
        else:
            print("Clave de cliente no válida.")

    except sqlite3.Error as e:
        print(f"Error al suspender al cliente: {e}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def recuperar_cliente():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente FROM Clientes WHERE Suspendido = 1")
        clientes_suspendidos = cursor.fetchall()

        if not clientes_suspendidos:
            print("No hay clientes suspendidos para recuperar.")
            return

        print("Clientes suspendidos:")
        for clave, nombre in clientes_suspendidos:
            print(f"{clave}: {nombre}")

        clave_cliente = input("Ingrese la clave del cliente que desea recuperar (0 para volver al menú anterior): ")
        
        if clave_cliente == '0':
            print("Redirigiendo al menú de clientes... ")
            return
        
        if not clave_cliente.isdigit():
            print("Clave de cliente no válida.")
            return
        
        clave_cliente = int(clave_cliente)

        cliente_valido = False
        for clave, _ in clientes_suspendidos:
            if clave_cliente == clave:
                cliente_valido = True
                break

        if cliente_valido:
            cursor.execute("SELECT Nombre_Cliente, RFC, Correo FROM Clientes WHERE Clave_Cliente = ?", (clave_cliente,))
            nombre_cliente, rfc_cliente, correo_cliente = cursor.fetchone()

            print(f"Datos del cliente a recuperar:")
            print(f"Nombre: {nombre_cliente}")
            print(f"RFC: {rfc_cliente}")
            print(f"Correo: {correo_cliente}")

            confirmacion = input("¿Desea recuperar a este cliente? (S/N): ")

            if confirmacion.upper() == 'S':
                cursor.execute("UPDATE Clientes SET Suspendido = 0 WHERE Clave_Cliente = ?", (clave_cliente,))
                conexion.commit()
                print("Cliente recuperado con éxito. Ahora puede emitir notas nuevamente.")
            else:
                print("Operación cancelada.")
        else:
            print("Clave de cliente no válida.")

    except sqlite3.Error as e:
        print(f"Error al recuperar al cliente: {e}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def listar_clientes_por_clave():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()           
        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente, RFC, Correo FROM Clientes WHERE Suspendido = 0 ORDER BY Clave_Cliente")
        clientes = cursor.fetchall()
        
        if not clientes:
            print("No hay clientes registrados. Registre un cliente antes de crear una lista.")
            return
         
        df = pd.DataFrame(clientes, columns=["Clave_Cliente", "Nombre_Cliente", "RFC", "Correo"])
        
        df = df.sort_values(by='Clave_Cliente')
        
        print("Listado de clientes registrados ordenados por clave:")   
        print(df)
        
        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de clientes? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesPorClave_{fecha_actual}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesPorClave_{fecha_actual}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Consultas y reportes de clientes... ")
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de reportes.")
    except Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def listar_clientes_por_nombre():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()         
        cursor.execute("SELECT Clave_Cliente, Nombre_Cliente, RFC, Correo FROM Clientes WHERE Suspendido = 0 ORDER BY Nombre_Cliente")
        clientes = cursor.fetchall()

        if not clientes:
            print("No hay clientes registrados. Registre un cliente antes de crear una lista.")
            return
        
        df = pd.DataFrame(clientes, columns=["Clave_Cliente", "Nombre_Cliente", "RFC", "Correo"])
        
        df = df.sort_values(by='Nombre_Cliente')
        
        print("Listado de clientes registrados ordenados por nombre:")   
        print(df)
        
        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de clientes? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesPorNombre_{fecha_actual}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesPorNombre_{fecha_actual}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Consultas y reportes de clientes... ")                
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de reportes.")
    except Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception:
        print(f'Se produjo el siguiente error {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def menu_clientes():
    while True:
        print("\nMenú Clientes:")
        print("1. Agregar un cliente")
        print("2. Suspender un cliene")
        print("3. Recuperar un cliente")
        print("4. Consultas y reportes de clientes")
        print("5. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_cliente()
        elif opcion == "2":
            suspender_cliente()
        elif opcion == "3":
            recuperar_cliente()
        elif opcion == "4":
            while True:
                print("\nConsultas y reportes de clientes:")
                print("1. Listado de clientes registrados ordenados por clave")
                print("2. Listado de clientes registrados ordenados por nombre")
                print("3. Volver al menú anterior")

                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    listar_clientes_por_clave()
                elif reporte_opcion == "2":
                    listar_clientes_por_nombre()
                elif reporte_opcion == "3":
                    confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de clientes? (S. Si / N. No): ")
                    while confirmacion_salir.upper() not in ('S', 'N'):
                        print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                        confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de clientes? (S/N): ")

                    if confirmacion_salir.upper() == 'S':
                        print("\nSaliendo de Consultas y reportes de clientes...")
                        break  
                    elif confirmacion_salir.upper() == 'N':
                        print("\nVolviendo al menú anterior...")
                        continue
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "5":
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

def agregar_servicio():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()        
        nombre_servicio = None
        costo_servicio = None
        while nombre_servicio is None:
            nombre_servicio = input("Ingrese el nombre del servicio: ")
            if not nombre_servicio.strip():
                print("El nombre del servicio no puede estar vacío. Inténtelo de nuevo.")
                nombre_servicio = None

        print(f"Ingrese el precio del servicio. (A dos decimales).")
        while True:
            precio_servicio = input("Precio: ").strip()
            if re.match(r'^\d+(\.\d{1,2})?$', precio_servicio):
                precio = float(precio_servicio)
                break
            else:
                print("\nIngrese un precio válido (A dos decimales).")
                continue
            
        cursor.execute("INSERT INTO Servicios (Nombre_Servicio, Costo) VALUES (?, ?)",(nombre_servicio, precio))
        conexion.commit()
        print("Servicio registrado con éxito.")     
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def suspender_servicio():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio FROM Servicios WHERE Suspendido = 0")
        servicios_activos = cursor.fetchall()
        
        if not servicios_activos:
            print("No hay servicios activos para suspender.")
            return

        print("Servicios Activos:")
        for clave, nombre in servicios_activos:
            print(f"Clave: {clave}, Nombre: {nombre}")
        
        clave_seleccionada = input("Ingrese la clave del servicio a suspender (0 para volver): ")
        
        if clave_seleccionada == '0':
            print("Redirigiendo al menú de servicios... ")
            return
        
        if not clave_seleccionada.isdigit():
            print("Clave de servicio no válida.")
            return
        
        clave_seleccionada = int(clave_seleccionada)
        
        servicio_valido = False
        for clave, _ in servicios_activos:
            if clave_seleccionada == clave:
                servicio_valido = True
                break

        if not servicio_valido:
            print("Clave de servicio no válida.")
            return

        cursor.execute("SELECT * FROM Servicios WHERE Clave_Servicio = ? AND Suspendido = 0", (clave_seleccionada,))
        servicio = cursor.fetchone()
        
        if servicio is None:
            print("El servicio ya está suspendido.")
            return
        
        print("Datos del servicio a suspender:")
        print(f"Clave: {servicio[0]}")
        print(f"Nombre: {servicio[1]}")
        print(f"Costo: {servicio[2]}")
        
        confirmacion = input("¿Desea suspender este servicio? (S. Sí/ N. No): ")
        
        if confirmacion.upper() == "S":
            cursor.execute("UPDATE Servicios SET Suspendido = 1 WHERE Clave_Servicio = ?", (clave_seleccionada,))
            conexion.commit()
            print("Servicio suspendido con éxito.")
        else:
            print("Operación cancelada.")
        
    except sqlite3.Error as e:
        print(f"Error al suspender el servicio: {e}")
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def recuperar_servicio():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio FROM Servicios WHERE Suspendido = 1")
        servicios_suspendidos = cursor.fetchall()
        
        if not servicios_suspendidos:
            print("No hay servicios suspendidos para recuperar.")
            return
        
        print("Servicios Suspendidos:")
        for clave, nombre in servicios_suspendidos:
            print(f"Clave: {clave}, Nombre: {nombre}")
        
        clave_seleccionada = input("Ingrese la clave del servicio a recuperar (0 para volver): ")
        
        if clave_seleccionada == '0':
            print("Redirigiendo al menú servicios... ")
            return
        
        if not clave_seleccionada.isdigit():
            print("Clave de servicio no válida.")
            return
        
        clave_seleccionada = int(clave_seleccionada)
        
        servicio_valido = False
        for clave, _ in servicios_suspendidos:
            if clave_seleccionada == clave:
                servicio_valido = True
                break

        if not servicio_valido:
            print("Clave de servicio no válida.")
            return

        cursor.execute("SELECT * FROM Servicios WHERE Clave_Servicio = ? AND Suspendido = 1", (clave_seleccionada,))
        servicio = cursor.fetchone()
        
        if servicio is None:
            print("El servicio no está suspendido.")
            return
        
        print("Datos del servicio a recuperar:")
        print(f"Clave: {servicio[0]}")
        print(f"Nombre: {servicio[1]}")
        print(f"Costo: {servicio[2]}")
        
        confirmacion = input("¿Desea recuperar este servicio? (S. Sí/ N. No): ")
        
        if confirmacion.upper() == "S":
            cursor.execute("UPDATE Servicios SET Suspendido = 0 WHERE Clave_Servicio = ?", (clave_seleccionada,))
            conexion.commit()
            print("Servicio recuperado con éxito.")
        else:
            print("Operación cancelada.")
        
    except sqlite3.Error as e:
        print(f"Error al recuperar el servicio: {e}")
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()

def buscar_servicio_por_clave():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()         
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
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def buscar_servicio_por_nombre():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()         
        nombre_servicio = input("Ingrese el nombre del servicio a buscar: ")
        cursor.execute("SELECT Nombre_Servicio, Costo FROM Servicios WHERE UPPER(Nombre_Servicio) = UPPER(?)", (nombre_servicio,))
        servicio = cursor.fetchone()
        
        if servicio:
            print(f"Detalles del servicio (nombre '{nombre_servicio}'):")
            print(f"Nombre: {servicio[0]}")
            print(f"Costo: {servicio[1]}")
        else:
            print("Servicio no encontrado.")
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def listar_servicios_por_clave():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()         
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios WHERE Suspendido = 0 ORDER BY Clave_Servicio")
        servicios = cursor.fetchall()
        
        if not servicios:
            print("No se han encontrado servicios o se encuentran suspendidos.")
            return
        
        df = pd.DataFrame(servicios, columns=["Clave_Servicio", "Nombre_Servicio", "Costo"])
        
        df = df.sort_values(by='Clave_Servicio')
        
        print("Listado de servicios registrados ordenados por clave:")
        print(df)  


        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosPorClave_{fecha_actual}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosPorClave_{fecha_actual}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Consultas y reportes de servicios... ")                
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de reportes.")
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def listar_servicios_por_nombre():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()        
        cursor.execute("SELECT Clave_Servicio, Nombre_Servicio, Costo FROM Servicios WHERE Suspendido = 0 ORDER BY Nombre_Servicio")
        servicios = cursor.fetchall()

        if not servicios:
            print("No se han encontrado servicios o se encuentran suspendidos.")
            return
        
        df = pd.DataFrame(servicios, columns=["Clave_Servicio", "Nombre_Servicio", "Costo"])
        
        df = df.sort_values(by='Nombre_Servicio')
        
        print("Listado de servicios registrados ordenados por nombre:")
        print(df)  

        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de reportes? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual_procesada = obtener_fecha_actual().strftime("%d%m%Y")
                #fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosPorNombre_{fecha_actual_procesada}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual_procesada = obtener_fecha_actual().strftime("%d%m%Y")
                #fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosPorNombre_{fecha_actual_procesada}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Consultas y reportes de servicios... ")                                
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de reportes.")
    except Error as e:
        print(e)
    except Exception:
        print(f'Se produjo el siguiente error: {sys.exc_info()[0]}')
    finally:
        if conexion:
            conexion.close()
            
def menu_servicios():
    while True:
        print("\nMenú Servicios:")
        print("1. Agregar un servicio")
        print("2. Suspender un servicio")
        print("3. Recuperar un servicio")
        print("4. Consultas y reportes de servicios")
        print("5. Listado de servicios")
        print("6. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_servicio()
        
        elif opcion == "2":
            suspender_servicio()
        
        elif opcion == "3":
            recuperar_servicio()
            
        elif opcion == "4":
            while True:
                print("\nConsultas y reportes de servicios:")
                print("1. Búsqueda por clave de servicio")
                print("2. Búsqueda por nombre de servicio")
                print("3. Volver al menú anterior")
                
                reporte_opcion = input("Seleccione una opción: ")

                if reporte_opcion == "1":
                    buscar_servicio_por_clave()
                elif reporte_opcion == "2":
                    buscar_servicio_por_nombre()
                elif reporte_opcion == "3":
                    confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de servicios? (S. Si / N. No): ")
                    while confirmacion_salir.upper() not in ('S', 'N'):
                        print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                        confirmacion_salir = input("¿Está seguro que desea salir de Consultas y reportes de servicios? (S/N): ")

                    if confirmacion_salir.upper() == 'S':
                        print("\nSaliendo de Consultas y reportes de servicios...")
                        break  
                    elif confirmacion_salir.upper() == 'N':
                        print("\nVolviendo al menú anterior...")
                        continue
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
                    
        elif opcion == "5":
            while True:
                print("\nListado de servicios:")
                print("1. Listado de servicios ordenados por clave")
                print("2. Listado de servicios ordenados por nombre de servicio")
                print("3. Volver al menú anterior")
                
                listado_opcion = input("Seleccione una opción: ")

                if listado_opcion == "1":
                    listar_servicios_por_clave()
                elif listado_opcion == "2":
                    listar_servicios_por_nombre()
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
                    
        elif opcion == "6":
            confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
            while confirmacion_salir.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion_salir = input("¿Está seguro que desea salir? (S/N): ")

            if confirmacion_salir.upper() == 'S':
                print("\nSaliendo del programa...")
                break  

            elif confirmacion_salir.upper() == 'N':
                print("\nRedirigiendo al menú principal...")
                continue
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def servicios_mas_prestados():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        cantidad = int(input("Ingrese la cantidad de servicios más prestados a identificar: "))
        if cantidad < 1:
            print("La cantidad debe ser al menos 1.")
            return

        fecha_actual = datetime.date.today()
        fecha_inicial = None
        fecha_final = None

        while fecha_inicial is None:
            fecha_inicial_input = input("Ingrese la fecha inicial del período (en formato DD-MM-YYYY): ")
            if fecha_inicial_input:
                try:
                    fecha_inicial = datetime.datetime.strptime(fecha_inicial_input, "%d-%m-%Y").date()
                    if fecha_inicial > fecha_actual:
                        print("\n*****ERROR: La fecha inicial no debe ser posterior a la fecha actual.*****")
                        fecha_inicial = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha inicial no se puede omitir. Ingrese la fecha inicial del período (en formato DD-MM-YYYY).")

        while fecha_final is None:
            fecha_final_input = input("Ingrese la fecha final del período (en formato DD-MM-YYYY): ")
            if fecha_final_input:
                try:
                    fecha_final = datetime.datetime.strptime(fecha_final_input, "%d-%m-%Y").date()
                    if fecha_final > fecha_actual or fecha_final < fecha_inicial:
                        print("\n*****ERROR: La fecha final no puede ser posterior a la fecha actual y debe ser mayor o igual a la fecha inicial.*****")
                        fecha_final = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha final no se puede omitir. Ingrese la fecha final del período (en formato DD-MM-YYYY).")

        consulta_sql = f"""
        SELECT s.Nombre_Servicio, COUNT(n.Folio) AS Cantidad
        FROM Notas n
        INNER JOIN Detalles_Nota d ON n.Folio = d.Folio
        INNER JOIN Servicios s ON d.Clave_Servicio = s.Clave_Servicio
        WHERE n.Fecha BETWEEN ? AND ?
        GROUP BY s.Nombre_Servicio
        ORDER BY Cantidad DESC
        LIMIT {cantidad}
        """
        
        cursor.execute(consulta_sql, (fecha_inicial, fecha_final))
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos disponibles para los parámetros proporcionados.")
            return

        print(f"Los {cantidad} servicios más prestados en el período:")
        #for resultado in resultados:
            #print(f"Nombre del Servicio: {resultado[0]}, Cantidad: {resultado[1]}")
        df = pd.DataFrame(resultados, columns=["Nombre del servicio", "Cantidad"])
        
        print(df)
        
        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de estadísticas? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosMasPrestados_{fecha_inicial}_{fecha_actual}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteServiciosMasPrestados_{fecha_inicial}_{fecha_actual}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Estadísticas... ")                
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de Estadísticas.")            
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception as ex:
        print(f'Se produjo el siguiente error: {ex}')
    finally:
        if conexion:
            conexion.close()
            
def clientes_con_mas_notas():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        cantidad = int(input("Ingrese la cantidad de clientes con más notas a identificar: "))
        if cantidad < 1:
            print("La cantidad debe ser al menos 1.")
            return

        fecha_actual = datetime.date.today()
        fecha_inicial = None
        fecha_final = None

        while fecha_inicial is None:
            fecha_inicial_input = input("Ingrese la fecha inicial del período (en formato DD-MM-YYYY): ")
            if fecha_inicial_input:
                try:
                    fecha_inicial = datetime.datetime.strptime(fecha_inicial_input, "%d-%m-%Y").date()
                    if fecha_inicial > fecha_actual:
                        print("\n*****ERROR: La fecha inicial no debe ser posterior a la fecha actual.*****")
                        fecha_inicial = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha inicial no se puede omitir. Ingrese la fecha inicial del período (en formato DD-MM-YYYY).")

        while fecha_final is None:
            fecha_final_input = input("Ingrese la fecha final del período (en formato DD-MM-YYYY): ")
            if fecha_final_input:
                try:
                    fecha_final = datetime.datetime.strptime(fecha_final_input, "%d-%m-%Y").date()
                    if fecha_final > fecha_actual or fecha_final < fecha_inicial:
                        print("\n*****ERROR: La fecha final no puede ser posterior a la fecha actual y debe ser mayor o igual a la fecha inicial.*****")
                        fecha_final = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha final no se puede omitir. Ingrese la fecha final del período (en formato DD-MM-YYYY).")

        consulta_sql = f"""
        SELECT c.Nombre_Cliente, COUNT(n.Folio) AS Cantidad
        FROM Notas n
        INNER JOIN Clientes c ON n.Clave_Cliente = c.Clave_Cliente
        WHERE n.Fecha BETWEEN ? AND ?
        GROUP BY c.Nombre_Cliente
        ORDER BY Cantidad DESC
        LIMIT {cantidad}
        """

        cursor.execute(consulta_sql, (fecha_inicial, fecha_final))
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos disponibles para los parámetros proporcionados.")
            return

        print(f"Los {cantidad} clientes con más notas en el período:")
        #for resultado in resultados:
            #print(f"Nombre del Cliente: {resultado[0]}, Cantidad de Notas: {resultado[1]}")
        df = pd.DataFrame(resultados, columns=["Nombre del cliente", "Cantidad de notas"])
        print(df)
            
        while True:
            exportar_opcion = input("¿Desea exportar el reporte a un archivo CSV, Excel o regresar al menú de estadísticas? (1. CSV/ 2. Excel/ 3. Regresar): ")
            if exportar_opcion == "1":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesConMasNotas_{fecha_inicial}_{fecha_actual}.csv"
                df.to_csv(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "2":
                fecha_actual = obtener_fecha_actual()
                nombre_archivo = f"ReporteClientesConMasNotas_{fecha_inicial}_{fecha_actual}.xlsx"
                df.to_excel(nombre_archivo, index=False)
                print(f"El reporte ha sido exportado a '{nombre_archivo}'")
            elif exportar_opcion == "3":
                print("Redirigiendo al menú de Estadísticas... ")                
                return
            else:
                print("Opción no válida. Por favor, elija entre 1. CSV, 2. Excel o 3. regresar al menú de Estadísticas.")
                
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception as ex:
        print(f'Se produjo el siguiente error: {ex}')
    finally:
        if conexion:
            conexion.close()
            
def promedio_montos_notas():
    try:
        fecha_actual = datetime.date.today()
        fecha_inicial = None
        fecha_final = None

        while fecha_inicial is None:
            fecha_inicial_input = input("Ingrese la fecha inicial del período (en formato DD-MM-YYYY): ")
            if fecha_inicial_input:
                try:
                    fecha_inicial = datetime.datetime.strptime(fecha_inicial_input, "%d-%m-%Y").date()
                    if fecha_inicial > fecha_actual:
                        print("\n*****ERROR: La fecha inicial no debe ser posterior a la fecha actual.*****")
                        fecha_inicial = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha inicial no se puede omitir. Ingrese la fecha inicial del período (en formato DD-MM-YYYY).")

        while fecha_final is None:
            fecha_final_input = input("Ingrese la fecha final del período (en formato DD-MM-YYYY): ")
            if fecha_final_input:
                try:
                    fecha_final = datetime.datetime.strptime(fecha_final_input, "%d-%m-%Y").date()
                    if fecha_final > fecha_actual or fecha_final < fecha_inicial:
                        print("\n*****ERROR: La fecha final no puede ser posterior a la fecha actual y debe ser mayor o igual a la fecha inicial.*****")
                        fecha_final = None
                except ValueError:
                    print("\n*****ERROR: Ingrese una fecha válida en formato DD-MM-YYYY.*****")
            else:
                print("La Fecha final no se puede omitir. Ingrese la fecha final del período (en formato DD-MM-YYYY).")

        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()
        
        cursor.execute("SELECT Monto, Fecha FROM Notas")
        notas = cursor.fetchall()
        
        df_notas = pd.DataFrame(notas, columns=["Monto", "Fecha"])
        
        df_notas['Fecha'] = pd.to_datetime(df_notas['Fecha'], format="%d-%m-%Y").dt.date
        df_notas = df_notas[(df_notas['Fecha'] >= fecha_inicial) & (df_notas['Fecha'] <= fecha_final)]
        
        if df_notas.empty:
            print("No hay datos disponibles para los parámetros proporcionados.")
            return

        promedio = df_notas['Monto'].mean()

        print(f"El promedio de los montos de las notas en el período es: ${promedio:.2f}")

    except Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception as ex:
        print(f'Se produjo el siguiente error: {str(ex)}')
    finally:
        if conexion:
            conexion.close()
            
def menu_estadisticas():
    while True:
        print("\nMenú Estadísticas:")
        print("1. Servicios más prestados")
        print("2. Clientes con más notas")
        print("3. Promedio de montos de notas")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            servicios_mas_prestados()        
        elif opcion == "2":
            clientes_con_mas_notas()
        elif opcion == "3":
            promedio_montos_notas()
        elif opcion == "4":
            confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
            while confirmacion_salir.upper() not in ('S', 'N'):
                print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                confirmacion_salir = input("¿Está seguro que desea salir? (S/N): ")

            if confirmacion_salir.upper() == 'S':
                print("\nSaliendo del programa...")
                break  

            elif confirmacion_salir.upper() == 'N':
                print("\nRedirigiendo al menú principal...")
                continue
            
        else:
            print("Opción no valida. Seleccione una opción valida.")
def main():
    try:
        conexion = sqlite3.connect("PIA_SEMB_1799759.db")
        cursor = conexion.cursor()

        crear_tablas()
        
        while True:
            print("\nMenú Principal - Taller Mecánico Morales:")
            print("1. Menú Notas.")
            print("2. Menú Clientes")
            print("3. Menú Servicios")
            print("4. Menú Estadísticas")
            print("5. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                menu_notas()
            elif opcion == "2":
                menu_clientes()
            elif opcion == "3":
                menu_servicios()
            elif opcion == "4":
                menu_estadisticas()
            elif opcion == "5":
                confirmacion_salir = input("¿Está seguro que desea salir? (S. Si / N. No): ")
                while confirmacion_salir.upper() not in ('S', 'N'):
                    print("Opción no válida. Por favor, seleccione 'S' para confirmar la salida o 'N' para cancelar.")
                    confirmacion_salir = input("¿Está seguro que desea salir? (S/N): ")

                if confirmacion_salir.upper() == 'S':
                    print("\nSaliendo del programa...")
                    break  

                elif confirmacion_salir.upper() == 'N':
                    print("\nRedirigiendo al menú principal...")
                    continue

            else:
                print("\nOpción no válida. Por favor, seleccione una opción válida.")
    
    except Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    finally:
        if conexion:
            conexion.commit()
            conexion.close()

if __name__ == "__main__":
    main()









