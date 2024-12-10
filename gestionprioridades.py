import heapq
import json
from datetime import datetime


class SistemaDeTareas:
    def __init__(self, archivo_datos="tareas.json"):
        self.heap = []
        self.archivo_datos = archivo_datos
        self.cargar_datos()

    def agregar_tarea(self, nombre, prioridad, fecha_vencimiento, dependencias=[]):
        if not isinstance(prioridad, int) or not nombre or not fecha_vencimiento:
            print("Error: La prioridad debe ser un número, el nombre no puede estar vacío y la fecha debe ser válida.")
            return

        # Convertir fecha de vencimiento a un objeto datetime
        try:
            fecha = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        except ValueError:
            print("Error: La fecha debe estar en el formato 'YYYY-MM-DD'.")
            return

        tarea = {
            "nombre": nombre,
            "prioridad": prioridad,
            "fecha_vencimiento": fecha.strftime("%Y-%m-%d"),
            "dependencias": dependencias,
        }
        heapq.heappush(self.heap, (prioridad, fecha, tarea))
        self.guardar_datos()
        print(f"Tarea '{nombre}' añadida con prioridad {prioridad} y fecha de vencimiento {fecha_vencimiento}.")

    def mostrar_tareas(self, criterio="prioridad"):
        print("\nTareas pendientes:")
        if criterio == "prioridad":
            tareas_ordenadas = sorted(self.heap, key=lambda x: (x[0], x[1]))
        elif criterio == "fecha":
            tareas_ordenadas = sorted(self.heap, key=lambda x: (x[1], x[0]))
        else:
            print("Criterio no válido. Usando prioridad como predeterminado.")
            tareas_ordenadas = sorted(self.heap, key=lambda x: (x[0], x[1]))

        for prioridad, fecha, tarea in tareas_ordenadas:
            ejecutable = self.verificar_dependencias_automatico(tarea["dependencias"])
            estado = "Ejecutable" if ejecutable else "No ejecutable"
            print(f"{tarea['nombre']} - Prioridad: {prioridad}, Fecha: {tarea['fecha_vencimiento']}, Estado: {estado}, Dependencias: {tarea['dependencias']}")

    def completar_tarea(self, nombre):
        for i, (_, _, tarea) in enumerate(self.heap):
            if tarea["nombre"] == nombre:
                if not self.verificar_dependencias_automatico(tarea["dependencias"]):
                    print(f"No se puede completar la tarea '{nombre}': tiene dependencias sin resolver.")
                    return
                self.heap.pop(i)
                heapq.heapify(self.heap)
                self.guardar_datos()
                print(f"Tarea '{nombre}' marcada como completada.")
                return
        print(f"Tarea '{nombre}' no encontrada.")

    def obtener_tarea_mayor_prioridad(self):
        if not self.heap:
            print("No hay tareas pendientes.")
            return
        prioridad, fecha, tarea = self.heap[0]
        ejecutable = self.verificar_dependencias_automatico(tarea["dependencias"])
        estado = "Ejecutable" if ejecutable else "No ejecutable"
        print(f"Tarea de mayor prioridad: {tarea['nombre']} (Prioridad: {prioridad}, Fecha: {tarea['fecha_vencimiento']}, Estado: {estado})")

    def verificar_dependencias_automatico(self, dependencias):
        """
        Verifica automáticamente si las dependencias de una tarea están completadas.
        Devuelve True si todas las dependencias están completadas, False en caso contrario.
        """
        tareas_pendientes = [tarea["nombre"] for _, _, tarea in self.heap]
        return all(dep not in tareas_pendientes for dep in dependencias)

    def guardar_datos(self):
        with open(self.archivo_datos, "w") as archivo:
            json.dump([(p, f.strftime("%Y-%m-%d"), t) for p, f, t in self.heap], archivo)

    def cargar_datos(self):
        try:
            with open(self.archivo_datos, "r") as archivo:
                datos = json.load(archivo)
                self.heap = []
                for entrada in datos:
                    if len(entrada) == 3:  # Validar que cada entrada tenga 3 elementos
                        p, f, t = entrada
                        self.heap.append((p, datetime.strptime(f, "%Y-%m-%d"), t))
                    else:
                        print(f"Entrada corrupta ignorada: {entrada}")
                heapq.heapify(self.heap)
        except FileNotFoundError:
            self.heap = []
        except json.JSONDecodeError:
            print("Error al leer el archivo JSON. Se inicializará una lista vacía.")
            self.heap = []


# Programa principal
sistema = SistemaDeTareas()

while True:
    print("\n--- Sistema de Gestión de Tareas ---")
    print("1. Añadir tarea")
    print("2. Mostrar tareas")
    print("3. Marcar tarea como completada")
    print("4. Obtener tarea de mayor prioridad")
    print("5. Salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        nombre = input("Nombre de la tarea: ")
        try:
            prioridad = int(input("Prioridad de la tarea (número entero): "))
        except ValueError:
            print("La prioridad debe ser un número entero.")
            continue
        fecha_vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ")
        dependencias = input("Dependencias (separadas por comas, si las hay): ").split(",")
        dependencias = [dep.strip() for dep in dependencias if dep.strip()]
        sistema.agregar_tarea(nombre, prioridad, fecha_vencimiento, dependencias)

    elif opcion == "2":
        criterio = input("¿Mostrar tareas por 'prioridad' o 'fecha'?: ").strip().lower()
        sistema.mostrar_tareas(criterio)

    elif opcion == "3":
        nombre = input("Nombre de la tarea a completar: ")
        sistema.completar_tarea(nombre)

    elif opcion == "4":
        sistema.obtener_tarea_mayor_prioridad()

    elif opcion == "5":
        print("Saliendo del sistema. ¡Hasta pronto!")
        break

    else:
        print("Opción no válida. Intenta de nuevo.")
