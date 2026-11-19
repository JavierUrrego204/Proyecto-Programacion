# Interfaz gráfica de usuario (GUI) unificada para Virtual Lab (Inicio de sesión, Profesor y Estudiante)
# Implementa Programación Orientada a Objetos con herencia y polimorfismo (BasePanel, ProfessorView, StudentView),
# visor esquemático interactivo en Canvas y edición en tiempo real de componentes SPICE.
# Requiere: pip install requests PySpice
# Coloca este archivo junto a virtuallab_client.py y ejecuta: python virtuallab_interfaz.py

import ast  # Importa ast para interpretar listas de Python con comillas simples devueltas por el servidor
import inspect  # Importa inspect para inspeccionar los parametros de las funciones del cliente HTTP
import json  # Importa json para convertir cadenas JSON a diccionarios/listas y viceversa
import os  # Importa os para manejar rutas de archivos, verificar existencia y crear carpetas
import re  # Importa re para trabajar con expresiones regulares al analizar netlists SPICE
import shutil  # Importa shutil para copiar archivos y borrar carpetas temporales
import subprocess  # Importa subprocess para abrir el explorador de archivos en macOS y Linux
import sys  # Importa sys para detectar el sistema operativo actual (Windows, macOS o Linux)
import tempfile  # Importa tempfile para crear directorios temporales limpios
import threading  # Importa threading para ejecutar tareas de red en hilos secundarios sin bloquear la GUI
import tkinter as tk  # Importa tkinter con el alias tk para construir los componentes visuales
from tkinter import filedialog, messagebox, simpledialog, ttk  # Importa dialogos, alertas y widgets tematicos ttk
import zipfile  # Importa zipfile para comprimir y descomprimir archivos .zip de practicas
import virtuallab_client  # Importa el modulo cliente encargado de comunicarse con el servidor HTTP

client = virtuallab_client  # Crea el alias client apuntando al modulo virtuallab_client

URL = "http://127.0.0.1:80"  # Define la direccion URL por defecto del servidor local
SERVER_CONFIG_FILE = os.path.join("client", "server_config.json")  # Construye la ruta del archivo JSON de configuracion

BG = "#101827"  # Define el color hexadecimal de fondo principal azul muy oscuro
CARD = "#1d293b"  # Define el color hexadecimal para tarjetas, barras superiores y barra lateral
FIELD = "#111a29"  # Define el color hexadecimal para cajas de texto, tablas y consola
BLUE = "#3478d4"  # Define el color hexadecimal azul primario para botones y elementos activos
BLUE_HOVER = "#2864b8"  # Define el color hexadecimal azul oscuro al presionar un boton
GREEN = "#16a34a"  # Define el color hexadecimal verde para acciones de simulacion y asignacion grupal
AMBER = "#f59e0b"  # Define el color hexadecimal ambar para resaltar nodos y voltajes en el esquema
CYAN = "#38bdf8"  # Define el color hexadecimal cian para cables y valores electricos
WHITE = "#f4f7fb"  # Define el color hexadecimal blanco suave para titulos y textos principales
MUTED = "#a9b7ca"  # Define el color hexadecimal gris azulado para subtitulos y textos secundarios


# =============================================================================
# CLASE BASE PARA POLIMORFISMO DE VISTAS
# =============================================================================

# Clase base que define la interfaz polimorfica de los paneles de Virtual Lab
class BasePanel(tk.Frame):

    # Metodo constructor que inicializa el panel base y guarda la referencia a la aplicacion principal
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)  # Llama al constructor de tk.Frame asignando el color de fondo oscuro
        self.app = app  # Guarda la instancia principal VirtualLab para compartir estilos y metodos

    # Metodo polimorfico que debe ser implementado por cada clase hija para dibujar su vista
    def render(self):
        raise NotImplementedError("Cada panel debe implementar su propio método render().")  # Lanza excepcion si no se sobrescribe

    # Metodo polimorfico que permite recargar los datos del panel desde el servidor
    def refresh(self):
        pass  # Instruccion nula por defecto para vistas que no necesiten recarga


# =============================================================================
# CLASE 1: INTERFAZ DEL PROFESOR (Hereda de BasePanel y reutiliza VirtualLab)
# =============================================================================

# Clase encargada de gestionar la vista del profesor, sus clases, estudiantes y laboratorios
class ProfessorView(BasePanel):

    # Metodo constructor que inicializa los atributos encapsulados de la vista del profesor
    def __init__(self, parent, app, initial_labs_raw=None, title="Panel del profesor"):
        super().__init__(parent, app)  # Llama al constructor de la clase padre BasePanel
        self.__title = title  # Guarda el titulo principal del panel del profesor en un atributo privado
        self.__prof_section = "Laboratorios"  # Define la seccion activa por defecto al iniciar sesion
        self.__prof_labs = self._parse_labs(initial_labs_raw)  # Convierte la respuesta inicial en lista de tuplas de laboratorios
        self.__prof_users = []  # Inicializa una lista vacia para almacenar los estudiantes del profesor
        self.__prof_classes = ["Sin clase"]  # Inicializa la lista de clases con la categoria por defecto "Sin clase"
        self.__removed_students = set()  # Inicializa un conjunto vacio para registrar estudiantes eliminados localmente
        self.__selected_lab_path = ""  # Inicializa vacia la ruta del archivo local seleccionado para subir
        self.__main_body = None  # Inicializa en None el contenedor derecho donde cambian las subvistas
        self.__nav_widgets = {}  # Inicializa un diccionario vacio para guardar los botones del menu lateral

    # Propiedad de solo lectura que retorna una copia de la lista de laboratorios del profesor
    @property
    def prof_labs(self):
        return list(self.__prof_labs)  # Retorna una nueva lista copia de self.__prof_labs

    # Propiedad de solo lectura que retorna una copia de la lista de estudiantes del profesor
    @property
    def prof_users(self):
        return list(self.__prof_users)  # Retorna una nueva lista copia de self.__prof_users

    # Propiedad de solo lectura que retorna una copia de la lista de clases del profesor
    @property
    def prof_classes(self):
        return list(self.__prof_classes)  # Retorna una nueva lista copia de self.__prof_classes

    # Funcion que construye toda la interfaz grafica del profesor con barra lateral y area principal
    def render(self):
        self._load_local_roster()  # Carga desde disco las clases y estudiantes guardados previamente
        self.app.title(f"Virtual Lab - {self.__title} (ID: {self.app.user_id})")  # Cambia el titulo de la ventana principal

        sidebar = tk.Frame(self, bg=CARD, width=195)  # Crea el contenedor de la barra lateral izquierda de 195 px
        sidebar.pack(side="left", fill="y")  # Posiciona la barra lateral a la izquierda ocupando todo el alto
        sidebar.pack_propagate(False)  # Impide que los widgets internos modifiquen el ancho fijo de 195 px

        tk.Label(sidebar, text="⚗  VIRTUAL LAB", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 14, "bold")).pack(pady=(22, 24), padx=16, anchor="w")  # Crea y posiciona el titulo superior

        self.__nav_widgets = {}  # Reinicia el diccionario de referencias de los botones laterales
        menu_items = [  # Lista de tuplas (tipo_de_icono, etiqueta_visible) para generar el menu lateral
            ("home", "Inicio"),
            ("doc", "Laboratorios"),
            ("users", "Estudiantes"),
            ("user", "Perfil"),
        ]

        for icon_kind, label in menu_items:  # Ciclo for que recorre cada tupla de icono y etiqueta del menu
            active = (self.__prof_section == label)  # Evalua si la etiqueta actual coincide con la seccion activa
            row_bg = BLUE if active else CARD  # Asigna color azul si esta activa o color tarjeta si no lo esta
            row_fg = WHITE if active else MUTED  # Asigna texto blanco si esta activa o gris claro si no lo esta

            item = tk.Frame(sidebar, bg=row_bg, cursor="hand2", padx=12, pady=10)  # Crea la fila clicable de la opcion
            item.pack(fill="x", padx=12, pady=3)  # Posiciona la fila ocupando todo el ancho interior de la barra

            ic = self.app._draw_icon(item, icon_kind, bg_color=row_bg, fg_color=row_fg)  # Dibuja el icono vectorial en Canvas
            ic.pack(side="left", padx=(0, 10))  # Ubica el icono a la izquierda con margen derecho de 10 px
            lbl = tk.Label(item, text=label, bg=row_bg, fg=row_fg,
                           font=("Segoe UI", 10, "bold" if active else "normal"))  # Crea la etiqueta de texto del boton
            lbl.pack(side="left")  # Ubica el texto a la izquierda junto al icono

            self.__nav_widgets[label] = (item, ic, lbl)  # Guarda la tupla de widgets en el diccionario por nombre de seccion
            for w in (item, ic, lbl):  # Ciclo for que recorre el marco, el icono y el texto de la opcion
                w.bind("<Button-1>", lambda e, sec=label: self._switch_prof_section(sec))  # Asocia clic izquierdo al cambio de vista

        bottom = tk.Frame(sidebar, bg=CARD, padx=12, pady=16)  # Crea el contenedor inferior de la barra lateral
        bottom.pack(side="bottom", fill="x")  # Ancla el contenedor al borde inferior de la barra lateral
        self.app.make_button(bottom, "Cerrar sesión", self.app.logout, color="#3b4658").pack(fill="x")  # Agrega boton de salida

        self.__main_body = tk.Frame(self, bg=BG, padx=20, pady=18)  # Crea el panel derecho para las subvistas del profesor
        self.__main_body.pack(side="left", fill="both", expand=True)  # Expande el panel derecho para llenar la ventana

        self._render_current_section()  # Llama al metodo que dibuja la subvista activa inicial
        self._sync_students_in_background()  # Inicia la sincronizacion de estudiantes con el servidor en segundo plano

    # Implementacion polimorfica que actualiza laboratorios y estudiantes del profesor desde el servidor
    def refresh(self):
        # Funcion interna que ejecuta las consultas de red en un hilo secundario
        def task():
            labs = client.listProfessorsLabs(URL, self.app.user_id)  # Consulta al servidor los laboratorios cargados
            students = self._api_list_students(self.app.user_id)  # Consulta al servidor los estudiantes registrados
            return self._parse_labs(labs), self._parse_students(students)  # Retorna ambas listas normalizadas en una tupla

        # Funcion interna que actualiza la interfaz grafica cuando llegan los datos del servidor
        def on_done(data):
            labs, students = data  # Desempaqueta la tupla recibida en dos variables
            self.__prof_labs = labs  # Actualiza el atributo privado con la nueva lista de laboratorios
            if students:  # Condicional que evalua si la lista de estudiantes no esta vacia
                self._merge_server_students(students)  # Combina los estudiantes del servidor con los datos locales
            self._render_current_section()  # Redibuja la subvista actual para reflejar los cambios

        self.app._run_async(task, on_done)  # Ejecuta task en segundo plano y luego llama a on_done en el hilo principal

    # Funcion que retorna la ruta del archivo JSON local donde se guarda el listado del profesor
    def _roster_file(self):
        os.makedirs("client", exist_ok=True)  # Crea la carpeta client si aun no existe en el sistema
        return os.path.join("client", f"roster_prof_{self.app.user_id}.json")  # Une carpeta y nombre de archivo JSON por ID

    # Funcion que carga desde disco las clases, estudiantes agregados y estudiantes ocultados
    def _load_local_roster(self):
        path = self._roster_file()  # Obtiene la ruta del archivo JSON del profesor
        if not os.path.exists(path):  # Condicional que comprueba si el archivo JSON no existe en disco
            self.__prof_users = []  # Inicializa la lista de estudiantes vacia
            self.__prof_classes = ["Sin clase"]  # Inicializa la lista de clases con el valor por defecto
            self.__removed_students = set()  # Inicializa vacio el conjunto de eliminados
            return  # Finaliza la ejecucion de la funcion
        try:
            with open(path, "r", encoding="utf-8") as f:  # Abre el archivo JSON en modo lectura con codificacion UTF-8
                data = json.load(f)  # Convierte el contenido del archivo JSON a un diccionario de Python

            loaded_classes = ["Sin clase"]  # Crea una lista base que siempre incluye "Sin clase"
            for cls_name in data.get("classes", []):  # Ciclo for que recorre la lista de clases guardadas en el JSON
                clean_cls = str(cls_name).strip()  # Convierte a cadena y elimina espacios al inicio y final
                if clean_cls and clean_cls not in loaded_classes:  # Condicional que evita agregar nombres vacios o repetidos
                    loaded_classes.append(clean_cls)  # Agrega la clase valida a la lista loaded_classes

            loaded_users = []  # Crea una lista vacia para reconstruir los registros de estudiantes
            for item in data.get("users", []):  # Ciclo for que recorre cada elemento de la lista users del JSON
                if len(item) >= 4:  # Condicional para registros que incluyen id, nombre, clase y rol
                    uid, uname, uclass, urole = str(item[0]), str(item[1]), str(item[2] or "Sin clase"), str(item[3])
                elif len(item) == 3:  # Condicional para registros antiguos que solo tenian id, nombre y rol
                    uid, uname, urole = str(item[0]), str(item[1]), str(item[2])
                    uclass = "Sin clase"  # Asigna la clase por defecto
                else:  # Caso contrario si el registro tiene menos de 3 elementos
                    continue  # Salta al siguiente elemento del ciclo for
                if uclass not in loaded_classes:  # Condicional que verifica si la clase del estudiante esta en la lista
                    loaded_classes.append(uclass)  # Agrega la clase faltante a loaded_classes
                loaded_users.append((uid, uname, uclass, urole))  # Agrega la tupla normalizada a loaded_users

            self.__prof_classes = loaded_classes  # Asigna las clases cargadas al atributo privado
            self.__prof_users = loaded_users  # Asigna los estudiantes cargados al atributo privado
            self.__removed_students = set(data.get("removed", []))  # Convierte la lista removed del JSON en un conjunto
        except Exception:  # Captura cualquier error de lectura o formato corrupto en el JSON
            self.__prof_users = []  # Restablece la lista de estudiantes a vacia
            self.__prof_classes = ["Sin clase"]  # Restablece las clases a su valor inicial
            self.__removed_students = set()  # Restablece el conjunto de eliminados a vacio

    # Funcion que guarda en disco las clases y estudiantes del profesor en formato JSON
    def _save_local_roster(self):
        if self.app.user_id is None:  # Condicional que verifica si no hay un profesor autenticado
            return  # Sale de la funcion sin escribir nada en disco
        try:
            with open(self._roster_file(), "w", encoding="utf-8") as f:  # Abre el archivo JSON en modo escritura
                json.dump(  # Escribe el diccionario serializado en el archivo JSON
                    {
                        "classes": self.__prof_classes,  # Guarda la lista de clases
                        "users": [list(u) for u in self.__prof_users],  # Convierte cada tupla de estudiante en lista
                        "removed": sorted(self.__removed_students),  # Ordena y convierte el conjunto de eliminados en lista
                    },
                    f,
                    ensure_ascii=False,  # Permite escribir tildes y caracteres especiales sin escapar
                    indent=2,  # Aplica sangria de 2 espacios para legibilidad
                )
        except Exception:  # Ignora errores si el sistema de archivos impide escribir
            pass  # Instruccion nula para continuar sin detener la interfaz

    # Funcion que valida contra el servidor que el estudiante exista antes de agregarlo a una clase
    def _verify_student_exists(self, student_id, student_name=""):
        if student_id == self.app.user_id:  # Condicional que impide que el profesor agregue su propio ID como alumno
            return False, "ID incorrecto o no existe: ese ID pertenece a tu cuenta de profesor."

        uid_str = str(student_id)  # Convierte el ID numerico a cadena de texto
        clean_name = student_name.strip().lower()  # Limpia espacios y pasa el nombre a minusculas

        for existing_id, existing_name, _, _ in self.__prof_users:  # Ciclo for que recorre los estudiantes ya guardados
            if existing_id == uid_str and clean_name and existing_name.strip().lower() != clean_name:  # Valida conflicto de ID
                return False, f"ID incorrecto: el ID {uid_str} ya está asignado a '{existing_name}'."

        server_raw = self._api_list_students(self.app.user_id)  # Solicita al servidor la lista actual de estudiantes
        server_list = self._parse_students(server_raw)  # Normaliza la respuesta del servidor a lista de tuplas

        explicit_ids = {uid: uname for uid, uname, _, _ in server_list if uid != "-"}  # Crea diccionario {id: nombre}
        if explicit_ids:  # Condicional que evalua si el servidor envio IDs explicitos
            if uid_str not in explicit_ids:  # Condicional que verifica si el ID ingresado existe en el diccionario
                return False, "ID incorrecto o no existe en el sistema."
            srv_name = explicit_ids[uid_str].strip().lower()  # Normaliza el nombre registrado en el servidor
            if clean_name and srv_name not in ("", "estudiante", "sin nombre") and srv_name != clean_name:  # Valida coincidencia
                return False, f"El ID {uid_str} pertenece a '{explicit_ids[uid_str]}', no a '{student_name}'."
            return True, "OK"  # Retorna exito si el ID y nombre coinciden

        server_names = {  # Crea conjunto por comprension con los nombres validos devueltos por el servidor
            uname.strip().lower()
            for _, uname, _, _ in server_list
            if uname and uname.strip().lower() not in ("", "estudiante", "sin nombre")
        }
        if server_names:  # Condicional cuando el servidor devuelve una lista de nombres sin IDs
            if clean_name and clean_name in server_names:  # Verifica si el nombre ingresado existe en el conjunto
                return True, "OK"
            if clean_name:  # Condicional si el nombre no se encontro en el servidor
                return False, f"ID incorrecto o estudiante no existe: '{student_name}' no está registrado en el servidor."

        return True, "OK"  # Retorna validacion positiva si supera las comprobaciones

    # Funcion que combina los estudiantes recibidos del servidor con las clases e IDs guardados localmente
    def _merge_server_students(self, server_students):
        known_info = {  # Diccionario por comprension que indexa datos locales por nombre en minusculas
            uname.lower(): (uid, uclass, urole)
            for uid, uname, uclass, urole in self.__prof_users
            if uid != "-"
        }
        merged = []  # Lista vacia donde se almacenaran los estudiantes fusionados
        seen_names = set()  # Conjunto vacio para controlar nombres ya agregados
        seen_ids = set()  # Conjunto vacio para controlar IDs ya agregados

        for uid, uname, uclass, urole in server_students:  # Ciclo for que recorre cada estudiante recibido del servidor
            key_name = uname.lower()  # Convierte el nombre a minusculas para usarlo como clave
            if key_name in self.__removed_students or uid in self.__removed_students:  # Condicional que omite eliminados
                continue  # Salta al siguiente estudiante
            if uid == "-" and key_name in known_info:  # Condicional si el servidor no envio ID pero existe en cache local
                saved_id, saved_class, saved_role = known_info[key_name]  # Recupera ID, clase y rol locales
                merged.append((saved_id, uname, saved_class, saved_role))  # Agrega la tupla completa a merged
                seen_ids.add(saved_id)  # Registra el ID como procesado
            else:  # Caso contrario cuando el servidor envio ID o no existe en cache local
                final_class = known_info[key_name][1] if key_name in known_info else uclass  # Conserva la clase local si existe
                merged.append((uid, uname, final_class, urole))  # Agrega la tupla a merged
                if uid != "-":  # Condicional que registra el ID si es valido
                    seen_ids.add(uid)  # Agrega el ID al conjunto de vistos
            seen_names.add(key_name)  # Agrega el nombre al conjunto de vistos

        for uid, uname, uclass, urole in self.__prof_users:  # Ciclo for que recorre los estudiantes locales restantes
            key_name = uname.lower()  # Convierte el nombre a minusculas
            if key_name in self.__removed_students or uid in self.__removed_students:  # Omite estudiantes eliminados
                continue  # Salta al siguiente registro
            if uid not in seen_ids and key_name not in seen_names:  # Condicional para evitar duplicados ya incluidos
                merged.append((uid, uname, uclass, urole))  # Conserva el estudiante agregado manualmente

        self.__prof_users = merged  # Actualiza la lista maestra de estudiantes del profesor
        self._save_local_roster()  # Guarda el listado combinado en el archivo JSON local

    # Funcion que consulta la lista de estudiantes en segundo plano al entrar al panel del profesor
    def _sync_students_in_background(self):
        # Funcion interna que consulta y normaliza los estudiantes en hilo secundario
        def task():
            return self._parse_students(self._api_list_students(self.app.user_id))

        # Funcion interna que actualiza la vista si la consulta devolvio estudiantes
        def on_done(students):
            if students:  # Condicional que verifica si se recibieron estudiantes
                self._merge_server_students(students)  # Fusiona los resultados con el listado local
                if self.__prof_section in ("Inicio", "Estudiantes"):  # Condicional que redibuja solo si la vista los muestra
                    self._render_current_section()  # Refresca la subvista activa

        self.app._run_async(task, on_done)  # Ejecuta la sincronizacion asincrona

    # Funcion adaptadora que llama a listStudents respetando la firma de parametros del cliente
    def _api_list_students(self, uid=None):
        target_id = self.app.user_id if uid is None else uid  # Selecciona el ID proporcionado o el del usuario activo
        if not hasattr(client, "listStudents"):  # Condicional que comprueba si el modulo cliente tiene listStudents
            return []  # Retorna lista vacia si la funcion no existe
        sig = inspect.signature(client.listStudents)  # Obtiene la firma de parametros de listStudents
        if len(sig.parameters) >= 2:  # Condicional si la funcion recibe URL e ID de profesor
            return client.listStudents(URL, target_id)  # Llama pasando URL y target_id
        return client.listStudents(URL)  # Llama pasando unicamente la URL

    # Funcion que empaqueta un laboratorio en formato .zip temporal y lo envia al servidor
    def _api_upload_lab(self, lab_name, file_path):
        clean_name = os.path.basename(lab_name.strip())  # Obtiene el nombre base limpio sin rutas
        if not clean_name.lower().endswith(".zip"):  # Condicional que verifica si falta la extension .zip
            clean_name += ".zip"  # Agrega la extension .zip al final del nombre

        temp_dir = tempfile.mkdtemp(prefix="vlab_upload_")  # Crea una carpeta temporal en el sistema operativo
        temp_zip_path = os.path.join(temp_dir, clean_name)  # Construye la ruta completa del archivo .zip temporal
        try:
            if zipfile.is_zipfile(file_path):  # Condicional que evalua si el archivo seleccionado ya es un .zip valido
                shutil.copy2(file_path, temp_zip_path)  # Copia el archivo .zip directamente a la ruta temporal
            else:  # Caso contrario si el profesor eligio un archivo individual (.cir, .py, .txt, etc.)
                with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:  # Crea un nuevo archivo .zip comprimido
                    zf.write(file_path, arcname=os.path.basename(file_path))  # Empaqueta el archivo dentro del .zip

            sig = inspect.signature(client.uploadLab)  # Inspecciona los parametros que acepta uploadLab
            params = [p.lower() for p in sig.parameters.keys()]  # Lista con los nombres de parametros en minusculas
            if len(params) >= 4:  # Condicional para clientes que esperan 4 argumentos
                if "file" in params[2] or "path" in params[2]:  # Verifica el orden de ruta y nombre
                    return client.uploadLab(URL, self.app.user_id, temp_zip_path, clean_name)
                return client.uploadLab(URL, self.app.user_id, clean_name, temp_zip_path)
            return client.uploadLab(URL, self.app.user_id, temp_zip_path)  # Llamada estandar con 3 argumentos
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)  # Elimina siempre la carpeta temporal al finalizar

    # Funcion adaptadora que llama a assignLab respetando el orden de parametros del modulo cliente
    def _api_assign_lab(self, student_id, lab_name):
        sig = inspect.signature(client.assignLab)  # Inspecciona la firma de assignLab en virtuallab_client
        params = [p.lower() for p in sig.parameters.keys()]  # Lista con los nombres de los parametros en minusculas
        if len(params) >= 4:  # Condicional cuando recibe 4 parametros
            if "lab" in params[2]:  # Condicional si el tercer parametro corresponde al nombre del laboratorio
                return client.assignLab(URL, self.app.user_id, lab_name, student_id)
            return client.assignLab(URL, self.app.user_id, student_id, lab_name)
        if len(params) == 3:  # Condicional cuando recibe 3 parametros
            if "lab" in params[1]:  # Condicional si el segundo parametro corresponde al laboratorio
                return client.assignLab(URL, lab_name, student_id)
            return client.assignLab(URL, student_id, lab_name)
        return client.assignLab(URL, self.app.user_id, student_id, lab_name)  # Llamada por defecto

    # Metodo estatico que normaliza la respuesta de laboratorios del servidor en tuplas (nombre, estado)
    @staticmethod
    def _parse_labs(raw):
        if not raw:  # Condicional que retorna lista vacia si raw es None o vacio
            return []
        if isinstance(raw, str):  # Condicional que evalua si raw es una cadena de texto
            text = raw.strip()  # Limpia espacios y saltos de linea
            if not text or text.lower() == "error":  # Retorna lista vacia si el servidor respondio "error"
                return []
            try:
                raw = json.loads(text)  # Intenta decodificar la cadena como JSON
            except Exception:  # Si falla JSON, intenta evaluarlo como literal de Python
                try:
                    raw = ast.literal_eval(text)  # Evalua listas con comillas simples
                except Exception:  # Si tampoco es literal Python, separa por lineas
                    lines = [line.strip() for line in text.splitlines() if line.strip()]  # Lista de lineas no vacias
                    return [(line, "Cargado") for line in lines]  # Retorna lista de tuplas (linea, "Cargado")

        if isinstance(raw, dict):  # Condicional si la respuesta es un diccionario
            if "error" in str(raw.get("status", "")).lower():  # Verifica si el diccionario reporta error
                return []
            raw = raw.get("labs") or raw.get("laboratories") or list(raw.values())  # Extrae la lista interna

        parsed = []  # Lista vacia para acumular las tuplas normalizadas
        if isinstance(raw, list):  # Condicional que verifica si raw ya es una lista
            for item in raw:  # Ciclo for que recorre cada elemento de la lista
                if isinstance(item, dict):  # Condicional si el elemento es un diccionario
                    name = item.get("name") or item.get("lab_name") or item.get("title") or str(item)  # Extrae nombre
                    date = item.get("date") or item.get("created_at") or "Cargado"  # Extrae fecha o estado
                    parsed.append((str(name), str(date)))  # Agrega la tupla (nombre, estado)
                elif isinstance(item, (list, tuple)) and len(item) >= 1:  # Condicional si el elemento es tupla o sublista
                    name = str(item[0])  # Toma el primer elemento como nombre
                    date = str(item[1]) if len(item) > 1 else "Cargado"  # Toma el segundo elemento o "Cargado"
                    parsed.append((name, date))  # Agrega la tupla normalizada
                else:  # Caso contrario cuando el elemento es una cadena simple
                    val = str(item).strip()  # Limpia espacios
                    if val:  # Condicional que verifica que no sea cadena vacia
                        parsed.append((val, "Cargado"))  # Agrega (nombre_archivo, "Cargado")
        return parsed  # Retorna la lista final de tuplas

    # Metodo estatico que normaliza la respuesta de estudiantes del servidor en tuplas (id, nombre, clase, rol)
    @staticmethod
    def _parse_students(raw):
        if not raw:  # Condicional que retorna lista vacia si no hay datos
            return []
        if isinstance(raw, str):  # Condicional si la respuesta viene como cadena de texto
            text = raw.strip()  # Elimina espacios sobrantes
            if not text or text.lower() == "error":  # Retorna vacio si el servidor devolvio error
                return []
            try:
                raw = json.loads(text)  # Intenta decodificar JSON
            except Exception:
                try:
                    raw = ast.literal_eval(text)  # Intenta evaluar lista literal de Python
                except Exception:
                    parsed = []  # Lista temporal para lineas separadas por comas
                    for line in text.splitlines():  # Ciclo for que recorre cada linea de texto
                        parts = [p.strip() for p in line.split(",") if p.strip()]  # Divide cada linea por comas
                        if len(parts) >= 2:  # Condicional si hay al menos dos columnas
                            if not parts[0].isdigit() and parts[1].isdigit():  # Detecta orden (nombre, id)
                                uname, uid = parts[0], parts[1]
                            else:  # Orden estandar (id, nombre)
                                uid, uname = parts[0], parts[1]
                            rol_txt = "Profesor" if len(parts) > 2 and "prof" in parts[2].lower() else "Estudiante"
                            parsed.append((uid, uname, "Sin clase", rol_txt))  # Agrega la tupla normalizada
                        elif parts:  # Condicional si solo viene un dato en la linea
                            if parts[0].isdigit():  # Si es numerico corresponde a un ID
                                parsed.append((parts[0], "Estudiante", "Sin clase", "Estudiante"))
                            else:  # Si es texto corresponde a un nombre sin ID
                                parsed.append(("-", parts[0], "Sin clase", "Estudiante"))
                    return parsed  # Retorna los registros interpretados

        if isinstance(raw, dict):  # Condicional si la respuesta es un diccionario
            if "error" in str(raw.get("status", "")).lower():  # Retorna vacio si reporta error
                return []
            for key in ("students", "users", "data", "items"):  # Ciclo for para buscar la clave contenedora
                if key in raw and isinstance(raw[key], (list, dict)):
                    raw = raw[key]
                    break  # Sale del ciclo al encontrar la coleccion
            if isinstance(raw, dict):  # Si sigue siendo diccionario {id: datos}, lo convierte a lista
                converted = []
                for k, v in raw.items():
                    if isinstance(v, dict):
                        entry = dict(v)
                        entry.setdefault("id", k)
                        converted.append(entry)
                    else:
                        converted.append((k, v))
                raw = converted

        parsed = []  # Lista final de tuplas (id, nombre, clase, rol)
        if isinstance(raw, list):  # Condicional que recorre la lista de usuarios
            for item in raw:
                if isinstance(item, dict):  # Si cada usuario es un diccionario
                    uid_val = next(
                        (item[k] for k in ("id", "user_id", "student_id", "uid") if item.get(k) is not None and str(item.get(k)).strip() != ""),
                        "-",
                    )
                    name_val = next(
                        (item[k] for k in ("name", "nombre", "username", "user", "full_name") if item.get(k) is not None and str(item.get(k)).strip() != ""),
                        "Sin nombre",
                    )
                    cls_val = str(item.get("class") or item.get("clase") or "Sin clase")
                    raw_rol = str(item.get("role") or item.get("rol") or "student").lower()
                    urole = "Profesor" if "prof" in raw_rol else "Estudiante"
                    parsed.append((str(uid_val), str(name_val), cls_val, urole))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:  # Si cada usuario es una tupla o lista
                    first, second = str(item[0]).strip(), str(item[1]).strip()
                    if not first.isdigit() and second.isdigit():
                        uname, uid = first, second
                    else:
                        uid, uname = first, second
                    raw_rol = str(item[2]).lower() if len(item) > 2 else "student"
                    urole = "Profesor" if "prof" in raw_rol else "Estudiante"
                    parsed.append((uid, uname, "Sin clase", urole))
                else:  # Si cada usuario es una cadena simple (ej. nombre devuelto por listStudents)
                    val = str(item).strip()
                    if not val:
                        continue
                    if val.isdigit():
                        parsed.append((val, "Estudiante", "Sin clase", "Estudiante"))
                    else:
                        parsed.append(("-", val, "Sin clase", "Estudiante"))
        return parsed  # Retorna la lista normalizada

    # Funcion que actualiza el color azul de la opcion activa en el menu lateral izquierdo
    def _update_sidebar_highlight(self):
        for label, (item, ic, lbl) in self.__nav_widgets.items():  # Ciclo for que recorre cada item del menu
            active = (self.__prof_section == label)  # Determina si este item es el seleccionado
            row_bg = BLUE if active else CARD  # Elige color azul o color de barra lateral
            row_fg = WHITE if active else MUTED  # Elige color de texto blanco o gris claro
            item.configure(bg=row_bg)  # Aplica el color de fondo al contenedor
            ic.configure(bg=row_bg)  # Aplica el color de fondo al Canvas del icono
            for shape in ic.find_all():  # Ciclo for que recorre las figuras vectoriales dibujadas en el icono
                if ic.type(shape) == "line":  # Condicional si la figura es una linea
                    ic.itemconfigure(shape, fill=row_fg)  # Cambia el color de relleno de la linea
                else:  # Caso contrario si es poligono, ovalo o arco
                    ic.itemconfigure(shape, outline=row_fg)  # Cambia el color del contorno
            lbl.configure(
                bg=row_bg,
                fg=row_fg,
                font=("Segoe UI", 10, "bold" if active else "normal"),
            )

    # Funcion que cambia la subvista activa del profesor sin reconstruir toda la ventana
    def _switch_prof_section(self, section):
        if self.__prof_section == section:  # Condicional que evita recargar si ya esta en esa seccion
            return
        self.__prof_section = section  # Actualiza el nombre de la seccion activa
        self._update_sidebar_highlight()  # Actualiza el resaltado visual en la barra lateral
        self._render_current_section()  # Dibuja el contenido de la nueva seccion

    # Funcion que limpia el panel derecho y renderiza la subvista correspondiente del profesor
    def _render_current_section(self):
        if self.__main_body is None or not self.__main_body.winfo_exists():  # Verifica que el contenedor derecho siga activo
            return
        for widget in self.__main_body.winfo_children():  # Ciclo for que destruye los widgets de la subvista anterior
            widget.destroy()

        if self.__prof_section == "Laboratorios":  # Condicional para mostrar la vista de laboratorios
            self._render_prof_labs(self.__main_body)
        elif self.__prof_section == "Estudiantes":  # Condicional para mostrar la vista de estudiantes y clases
            self._render_prof_students(self.__main_body)
        elif self.__prof_section == "Perfil":  # Condicional para mostrar los datos de perfil
            self._render_prof_profile(self.__main_body)
        else:  # Caso por defecto ("Inicio")
            self._render_prof_home(self.__main_body)

    # Funcion que construye la pantalla de inicio del profesor con tarjetas resumen
    def _render_prof_home(self, body):
        tk.Label(body, text=self.__title, bg=BG, fg=WHITE,
                 font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x")  # Titulo principal
        tk.Label(body, text=f"Usuario ID: {self.app.user_id}  ·  Servidor: {URL}", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(2, 18))  # Subtitulo con ID y servidor

        cards = tk.Frame(body, bg=BG)  # Contenedor horizontal para las tarjetas de resumen
        cards.pack(fill="x")

        active_classes_count = len([c for c in self.__prof_classes if c != "Sin clase"])  # Cuenta las clases creadas
        for card_title, count, btn_txt, target in [  # Ciclo for que crea las 3 tarjetas estadisticas
            ("Laboratorios cargados", str(len(self.__prof_labs)), "Ir a Laboratorios", "Laboratorios"),
            ("Estudiantes en lista", str(len(self.__prof_users)), "Ir a Estudiantes", "Estudiantes"),
            ("Clases creadas", str(active_classes_count), "Gestionar clases", "Estudiantes"),
        ]:
            c = tk.Frame(cards, bg=CARD, padx=20, pady=18)  # Crea la tarjeta oscura
            c.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(c, text=card_title, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")  # Titulo de la tarjeta
            tk.Label(c, text=count, bg=CARD, fg=WHITE,
                     font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x", pady=8)  # Numero indicador
            self.app.make_button(
                c, btn_txt, lambda sec=target: self._switch_prof_section(sec)
            ).pack(anchor="w")  # Boton de acceso directo a la seccion

    # Funcion que construye la vista de subida y asignacion de laboratorios del profesor
    def _render_prof_labs(self, body):
        cols = tk.Frame(body, bg=BG)  # Contenedor principal dividido en 2 columnas
        cols.pack(fill="both", expand=True)
        cols.columnconfigure(0, weight=4)  # Asigna peso 4 (40%) a la columna izquierda
        cols.columnconfigure(1, weight=6)  # Asigna peso 6 (60%) a la columna derecha
        cols.rowconfigure(0, weight=1)  # Permite que ambas columnas crezcan verticalmente

        left = tk.Frame(cols, bg=CARD, padx=18, pady=18)  # Tarjeta izquierda para subir practicas
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(left, text="Subir laboratorio", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x")
        tk.Label(left, text="Se empaquetará automáticamente en .zip para el servidor", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(2, 12))

        drop_canvas = tk.Canvas(left, height=165, bg=FIELD, highlightthickness=0, cursor="hand2")  # Recuadro clicable
        drop_canvas.pack(fill="x", pady=(0, 12))

        # Funcion interna que formatea el nombre y tamano en KB del archivo elegido
        def format_file_info(path):
            if not path or not os.path.exists(path):  # Condicional si aun no hay archivo valido seleccionado
                return "Formatos: .zip, .cir, .py, .txt"
            kb = max(1, os.path.getsize(path) // 1024)  # Calcula el tamano del archivo en kilobytes
            return f"{os.path.basename(path)} ({kb} KB)"  # Retorna nombre base y tamano

        selected_file_lbl = tk.StringVar(value=format_file_info(self.__selected_lab_path))  # Variable de texto observable

        lab_entry = tk.Entry(left, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                             relief="flat", font=("Segoe UI", 10))  # Campo para escribir el nombre de la practica

        # Funcion interna que abre el explorador para seleccionar un archivo local
        def choose_file(event=None):
            path = filedialog.askopenfilename(
                title="Seleccionar archivo de laboratorio",
                filetypes=[("Laboratorios", "*.zip *.cir *.py *.txt *.pdf"), ("Todos", "*.*")],
            )
            if path:  # Condicional que se ejecuta si el usuario selecciono un archivo
                self.__selected_lab_path = path  # Guarda la ruta completa del archivo
                fname = os.path.basename(path)  # Extrae el nombre del archivo sin directorio
                selected_file_lbl.set(format_file_info(path))  # Actualiza la etiqueta con el nombre y peso
                if not lab_entry.get().strip():  # Condicional para autocompletar el nombre si el campo esta vacio
                    lab_entry.insert(0, os.path.splitext(fname)[0])  # Inserta el nombre sin extension
                redraw_drop()  # Redibuja el Canvas con el estado actualizado

        btn_choose = self.app.make_button(drop_canvas, "Elegir archivo", choose_file, pady=7)  # Boton dentro del Canvas
        drop_canvas.bind("<Button-1>", choose_file)  # Permite hacer clic en todo el recuadro para elegir archivo

        # Funcion interna que dibuja el marco punteado y el icono de nube en el Canvas
        def redraw_drop(event=None):
            drop_canvas.delete("all")  # Borra los dibujos previos del Canvas
            w = drop_canvas.winfo_width() or 260  # Obtiene el ancho actual del Canvas
            cx = w // 2  # Calcula la coordenada X central
            drop_canvas.create_rectangle(4, 4, w - 4, 161, outline=BLUE, width=2, dash=(6, 4))  # Dibuja borde punteado azul
            drop_canvas.create_arc(cx - 22, 18, cx + 2, 42, start=40, extent=220,
                                   style="arc", outline=BLUE, width=2)  # Dibuja arco izquierdo de la nube
            drop_canvas.create_arc(cx - 8, 14, cx + 22, 42, start=-30, extent=210,
                                   style="arc", outline=BLUE, width=2)  # Dibuja arco derecho de la nube
            drop_canvas.create_line(cx - 14, 41, cx + 14, 41, fill=BLUE, width=2)  # Dibuja linea base de la nube
            drop_canvas.create_line(cx, 27, cx, 49, fill=BLUE, width=2)  # Dibuja linea vertical de la flecha
            drop_canvas.create_line(cx - 6, 33, cx, 27, cx + 6, 33, fill=BLUE, width=2)  # Dibuja punta de la flecha

            title_txt = "Archivo listo para subir" if self.__selected_lab_path else "Selecciona un archivo de laboratorio"
            drop_canvas.create_text(cx, 66, text=title_txt,
                                    fill=WHITE, font=("Segoe UI", 9, "bold"))  # Dibuja titulo de estado
            drop_canvas.create_text(cx, 85, text=selected_file_lbl.get(),
                                    fill=GREEN if self.__selected_lab_path else MUTED,
                                    font=("Segoe UI", 8, "bold" if self.__selected_lab_path else "normal"))
            drop_canvas.create_window(cx, 124, window=btn_choose)  # Posiciona el boton "Elegir archivo"

        drop_canvas.bind("<Configure>", redraw_drop)  # Redibuja el Canvas cada vez que cambie su tamano

        tk.Label(left, text="Nombre del laboratorio", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        lab_entry.pack(fill="x", ipady=8, pady=(5, 14))

        upload_btn = self.app.make_button(left, "Subir laboratorio", None)  # Crea el boton principal de subida

        # Funcion interna que valida los campos y sube el laboratorio al servidor en hilo secundario
        def upload_real_lab():
            name = lab_entry.get().strip()  # Obtiene el nombre ingresado sin espacios
            if not self.__selected_lab_path:  # Condicional que exige seleccionar un archivo primero
                messagebox.showwarning("Archivo faltante", "Primero elige un archivo para subir.")
                return
            if not name:  # Condicional que exige escribir un nombre para la practica
                messagebox.showwarning("Nombre faltante", "Ingresa un nombre para el laboratorio.")
                return

            file_path = self.__selected_lab_path  # Guarda localmente la ruta antes de iniciar el hilo
            upload_btn.configure(state="disabled", text="Subiendo...")  # Bloquea el boton durante la peticion

            def task():
                return self._api_upload_lab(name, file_path)  # Empaqueta en .zip y llama a client.uploadLab

            def on_done(resp):
                if upload_btn.winfo_exists():  # Verifica que el boton siga existiendo en pantalla
                    upload_btn.configure(state="normal", text="Subir laboratorio")  # Restaura el estado del boton
                if resp is None or resp is False or "error" in str(resp).lower():  # Condicional si el servidor rechazo la subida
                    messagebox.showerror("Error al subir", f"No se pudo subir el laboratorio:\n{resp}")
                    return

                self.__selected_lab_path = ""  # Limpia la ruta del archivo subido
                if lab_entry.winfo_exists():
                    lab_entry.delete(0, "end")  # Limpia el campo de nombre
                selected_file_lbl.set(format_file_info(""))  # Restaura el texto por defecto del recuadro
                redraw_drop()  # Redibuja el recuadro punteado
                messagebox.showinfo("Laboratorio cargado", f"'{name}' se subió correctamente.")
                self.refresh()  # Recarga la tabla de laboratorios disponibles

            def on_err(err):
                if upload_btn.winfo_exists():
                    upload_btn.configure(state="normal", text="Subir laboratorio")
                messagebox.showerror("Error de conexión", str(err))

            self.app._run_async(task, on_done, on_err)  # Ejecuta la subida sin congelar la ventana

        upload_btn.configure(command=upload_real_lab)  # Asocia la funcion upload_real_lab al boton
        upload_btn.pack(fill="x")

        right = tk.Frame(cols, bg=CARD, padx=18, pady=18)  # Tarjeta derecha con la tabla de practicas disponibles
        right.grid(row=0, column=1, sticky="nsew")

        header_bar = tk.Frame(right, bg=CARD)  # Cabecera de la tarjeta derecha
        header_bar.pack(fill="x")
        tk.Label(header_bar, text=f"Laboratorios disponibles ({len(self.__prof_labs)})", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(side="left")

        self.app.make_button(
            header_bar, "Actualizar", self.refresh,
            color="#3b4658", padx=10, pady=4,
        ).pack(side="right")  # Boton para refrescar manualmente la lista del servidor

        search_row = tk.Frame(right, bg=FIELD, padx=10)  # Contenedor del buscador de laboratorios
        search_row.pack(fill="x", pady=(10, 12))
        self.app._draw_icon(search_row, "search", bg_color=FIELD, fg_color=MUTED).pack(side="left")  # Icono de lupa
        search_ent = tk.Entry(search_row, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                              relief="flat", font=("Segoe UI", 10))  # Caja de texto para filtrar por nombre
        search_ent.pack(side="left", fill="x", expand=True, ipady=7, padx=(8, 0))

        tree_wrap = tk.Frame(right, bg=FIELD)  # Contenedor de la tabla Treeview
        tree_wrap.pack(fill="both", expand=True)

        tree = ttk.Treeview(  # Tabla Treeview con columnas de nombre y estado
            tree_wrap,
            columns=("nombre", "estado"),
            show="headings",
            style="Dark.Treeview",
            selectmode="browse",
        )
        tree.heading("nombre", text="Nombre del laboratorio", anchor="w")  # Encabezado de columna 1
        tree.heading("estado", text="Estado", anchor="w")  # Encabezado de columna 2
        tree.column("nombre", width=280, anchor="w")  # Ancho de columna 1
        tree.column("estado", width=110, anchor="w")  # Ancho de columna 2
        tree.pack(side="left", fill="both", expand=True)

        # Funcion interna que filtra y muestra los laboratorios en la tabla
        def populate_labs(filter_text=""):
            tree.delete(*tree.get_children())  # Elimina todas las filas actuales de la tabla
            q = filter_text.lower()  # Convierte el texto de busqueda a minusculas
            for lname, ldate in self.__prof_labs:  # Ciclo for que recorre cada laboratorio cargado
                if q in lname.lower():  # Condicional que comprueba si el nombre coincide con el filtro
                    tree.insert("", "end", values=(lname, ldate))  # Inserta una fila en la tabla

        populate_labs()  # Llena la tabla inicialmente con todos los laboratorios
        search_ent.bind("<KeyRelease>", lambda e: populate_labs(search_ent.get().strip()))  # Filtra al soltar cada tecla

        # Funcion interna que abre el dialogo de asignacion para el laboratorio seleccionado
        def assign_selected():
            sel = tree.selection()  # Obtiene la fila seleccionada en la tabla
            if not sel:  # Condicional que advierte si no hay ninguna fila seleccionada
                messagebox.showinfo("Selecciona uno", "Haz clic en un laboratorio de la tabla para asignarlo.")
                return
            lab_name = tree.item(sel[0], "values")[0]  # Obtiene el nombre del laboratorio de la primera columna
            self._open_assign_modal(lab_name)  # Abre la ventana modal de asignacion

        tree.bind("<Double-1>", lambda e: assign_selected())  # Permite abrir la asignacion con doble clic

        self.app.make_button(
            right, "Asignar laboratorio seleccionado", assign_selected, pady=8
        ).pack(fill="x", pady=(10, 0))

    # Funcion que despliega la ventana modal para asignar una practica a un estudiante o a toda una clase
    def _open_assign_modal(self, lab_name):
        modal = tk.Toplevel(self)  # Crea una ventana secundaria emergente sobre la ventana principal
        modal.title("Asignar laboratorio")  # Define el titulo de la ventana modal
        modal.geometry("430x340")  # Define el tamano fijo de la ventana modal
        modal.configure(bg=CARD)  # Aplica el color oscuro de tarjeta
        modal.transient(self)  # Vincula la ventana modal a la ventana padre
        modal.grab_set()  # Captura todos los eventos hasta que el usuario cierre el modal

        tk.Label(modal, text="Asignar práctica a estudiante", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=22, pady=(16, 2))
        tk.Label(modal, text=f"Laboratorio: {lab_name}", bg=CARD, fg=BLUE,
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=22, pady=(0, 12))

        tk.Label(modal, text="Filtrar por clase:", bg=CARD, fg=WHITE,
                 anchor="w").pack(fill="x", padx=22)
        class_filter = ttk.Combobox(  # Desplegable de solo lectura para elegir la clase a filtrar
            modal,
            values=["Todas las clases"] + self.__prof_classes,
            state="readonly",
        )
        class_filter.set("Todas las clases")  # Selecciona "Todas las clases" por defecto
        class_filter.pack(fill="x", padx=22, pady=(4, 10), ipady=3)

        tk.Label(modal, text="Estudiante (ID - Nombre [Clase]) o ingresa ID:", bg=CARD, fg=WHITE,
                 anchor="w").pack(fill="x", padx=22)
        combo = ttk.Combobox(modal, values=[])  # Desplegable editable con los estudiantes filtrados
        combo.pack(fill="x", padx=22, pady=(4, 6), ipady=4)

        selected_class_lbl = tk.Label(
            modal, text="Clase del estudiante: -", bg=CARD, fg=MUTED,
            font=("Segoe UI", 9, "bold"), anchor="w"
        )
        selected_class_lbl.pack(fill="x", padx=22, pady=(0, 14))

        # Funcion interna que retorna la lista de estudiantes que pertenecen a la clase elegida
        def get_filtered_students():
            chosen_cls = class_filter.get()  # Obtiene la clase seleccionada en el filtro
            if chosen_cls == "Todas las clases":  # Condicional si se muestran todos los estudiantes
                return list(self.__prof_users)
            return [u for u in self.__prof_users if u[2] == chosen_cls]  # Filtra por coincidencia de clase

        # Funcion interna que actualiza la etiqueta con la clase del estudiante seleccionado
        def update_student_class_info(event=None):
            raw_val = combo.get().strip()  # Obtiene el texto actual del desplegable
            raw_uid = raw_val.split("-")[0].strip()  # Extrae el ID ubicado antes del guion
            for uid, uname, uclass, _ in self.__prof_users:  # Busca el ID en la lista de estudiantes del profesor
                if uid == raw_uid and raw_uid != "-":
                    selected_class_lbl.configure(text=f"Clase del estudiante: {uclass}", fg=WHITE)
                    return
            selected_class_lbl.configure(text="Clase del estudiante: No asignada en lista", fg=MUTED)

        # Funcion interna que actualiza las opciones del desplegable de estudiantes al cambiar de clase
        def refresh_modal_students(event=None):
            filtered = get_filtered_students()  # Obtiene los alumnos de la clase filtrada
            choices = [f"{uid} - {uname} ({uclass})" for uid, uname, uclass, _ in filtered]  # Formatea cada opcion
            combo.configure(values=choices)  # Asigna las opciones al Combobox
            if choices:  # Condicional si existen estudiantes en la clase seleccionada
                combo.set(choices[0])  # Selecciona el primer estudiante de la lista
            else:  # Caso contrario si la clase no tiene estudiantes
                combo.set("")  # Deja el campo vacio
            update_student_class_info()  # Actualiza la etiqueta inferior de clase

        refresh_modal_students()  # Carga inicial de opciones en el modal
        class_filter.bind("<<ComboboxSelected>>", refresh_modal_students)  # Recarga al elegir otra clase
        combo.bind("<<ComboboxSelected>>", update_student_class_info)  # Actualiza clase al elegir alumno
        combo.bind("<KeyRelease>", update_student_class_info)  # Actualiza clase si el usuario escribe un ID manualmente

        btns = tk.Frame(modal, bg=CARD)  # Fila contenedora de los botones del modal
        btns.pack(fill="x", padx=22)
        confirm_btn = self.app.make_button(btns, "Asignar estudiante", None, pady=8)
        assign_class_btn = self.app.make_button(btns, "Asignar a clase", None, color=GREEN, pady=8)

        # Funcion interna que asigna el laboratorio al estudiante individual seleccionado
        def confirm_assign():
            raw_val = combo.get().strip()
            raw_uid = raw_val.split("-")[0].strip()
            if not raw_uid or raw_uid == "-":  # Condicional que valida que el estudiante tenga ID
                messagebox.showwarning(
                    "ID faltante",
                    "Este estudiante aún no tiene ID asignado. Agrégalo primero en la pestaña Estudiantes con su ID.",
                    parent=modal,
                )
                return
            if not raw_uid.isdigit() or len(raw_uid) > 10:  # Valida que el ID tenga solo digitos y maximo 10 numeros
                messagebox.showwarning(
                    "ID inválido",
                    "El ID debe contener solo números y tener máximo 10 dígitos.",
                    parent=modal,
                )
                return
            student_id = int(raw_uid)  # Convierte el ID validado a entero

            if student_id == self.app.user_id:  # Condicional que impide autoasignarse practicas
                messagebox.showerror("ID inválido", "Ese ID pertenece a tu cuenta de profesor.", parent=modal)
                return

            confirm_btn.configure(state="disabled", text="Asignando...")

            def task():
                return self._api_assign_lab(student_id, lab_name)  # Envia la peticion assignLab al servidor

            def on_done(resp):
                if confirm_btn.winfo_exists():
                    confirm_btn.configure(state="normal", text="Asignar estudiante")

                if resp is None or resp is False or "error" in str(resp).lower():  # Evalua si el servidor retorno error
                    messagebox.showerror(
                        "Error al asignar",
                        f"ID incorrecto o no existe en el sistema.\nDetalle del servidor: {resp}",
                        parent=modal,
                    )
                    return

                messagebox.showinfo(
                    "Asignación exitosa",
                    f"Laboratorio '{lab_name}' asignado al estudiante ID {student_id}.",
                    parent=modal,
                )
                if modal.winfo_exists():
                    modal.destroy()  # Cierra la ventana modal tras confirmar la asignacion

            def on_err(err):
                if confirm_btn.winfo_exists():
                    confirm_btn.configure(state="normal", text="Asignar estudiante")
                messagebox.showerror("Error de conexión", str(err), parent=modal)

            self.app._run_async(task, on_done, on_err)

        # Funcion interna que asigna el laboratorio a todos los estudiantes de la clase filtrada
        def confirm_assign_class():
            chosen_cls = class_filter.get()
            if chosen_cls == "Todas las clases":  # Condicional que exige seleccionar una clase especifica
                messagebox.showinfo("Elige una clase", "Selecciona primero una clase en el filtro superior.", parent=modal)
                return
            targets = [u for u in get_filtered_students() if u[0].isdigit()]  # Filtra alumnos con ID numerico valido
            if not targets:  # Condicional si la clase no tiene estudiantes con ID
                messagebox.showwarning("Clase vacía", f"No hay estudiantes con ID válido en '{chosen_cls}'.", parent=modal)
                return

            assign_class_btn.configure(state="disabled", text="Asignando...")

            def task():
                ok_count = 0  # Contador de asignaciones exitosas
                failed = []  # Lista de estudiantes cuya asignacion fallo
                for uid_str, uname, _, _ in targets:  # Ciclo for que asigna la practica a cada miembro de la clase
                    resp = self._api_assign_lab(int(uid_str), lab_name)
                    if resp is not None and resp is not False and "error" not in str(resp).lower():
                        ok_count += 1  # Incrementa el contador de exitos
                    else:
                        failed.append(f"{uname} ({uid_str})")  # Registra el fallo
                return ok_count, failed

            def on_done(result):
                ok_count, failed = result  # Desempaqueta el conteo de exitos y la lista de fallos
                if assign_class_btn.winfo_exists():
                    assign_class_btn.configure(state="normal", text="Asignar a clase")

                if ok_count == 0:  # Condicional si ninguna asignacion tuvo exito
                    messagebox.showerror("Error al asignar", "No se pudo asignar el laboratorio a la clase.", parent=modal)
                    return

                extra = f"\nFallaron: {', '.join(failed)}" if failed else ""
                messagebox.showinfo(
                    "Asignación por clase",
                    f"Laboratorio '{lab_name}' asignado a {ok_count} estudiante(s) de '{chosen_cls}'.{extra}",
                    parent=modal,
                )
                if modal.winfo_exists():
                    modal.destroy()

            def on_err(err):
                if assign_class_btn.winfo_exists():
                    assign_class_btn.configure(state="normal", text="Asignar a clase")
                messagebox.showerror("Error de conexión", str(err), parent=modal)

            self.app._run_async(task, on_done, on_err)

        confirm_btn.configure(command=confirm_assign)
        assign_class_btn.configure(command=confirm_assign_class)
        confirm_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        assign_class_btn.pack(side="left", fill="x", expand=True, padx=4)
        self.app.make_button(btns, "Cancelar", modal.destroy, color="#3b4658", pady=8).pack(
            side="left", fill="x", expand=True, padx=(4, 0)
        )

    # Funcion que construye la vista de creacion de clases y gestion de estudiantes del profesor
    def _render_prof_students(self, body):
        cols = tk.Frame(body, bg=BG)  # Contenedor de 2 columnas
        cols.pack(fill="both", expand=True)
        cols.columnconfigure(0, weight=4)
        cols.columnconfigure(1, weight=6)
        cols.rowconfigure(0, weight=1)

        left = tk.Frame(cols, bg=CARD, padx=18, pady=16)  # Panel izquierdo para crear clases y agregar alumnos
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(left, text="Crear clase", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")
        tk.Label(left, text="Clasifica a tus estudiantes por grupo o materia",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(1, 6))

        class_row = tk.Frame(left, bg=CARD)  # Fila horizontal para caja de texto y boton "Crear"
        class_row.pack(fill="x", pady=(0, 12))
        e_new_class = tk.Entry(class_row, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                               relief="flat", font=("Segoe UI", 10))
        e_new_class.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))

        tk.Frame(left, bg="#2b3a52", height=1).pack(fill="x", pady=(0, 12))  # Separador horizontal delgado

        tk.Label(left, text="Agregar estudiante", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
        tk.Label(left, text="Verifica el estudiante y asígnalo a una clase",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(1, 10))

        e_name = self.app.add_field(left, "Nombre del estudiante")  # Campo de texto para el nombre
        e_id = self.app.add_field(left, "ID del estudiante")  # Campo de texto para el ID
        vcmd_id = (tk.Misc.register(self, self.app._validate_id_input), "%P")  # Registra validacion de maximo 10 digitos
        e_id.configure(validate="key", validatecommand=vcmd_id)  # Bloquea letras o mas de 10 digitos al escribir

        tk.Label(left, text="Clase", bg=CARD, fg=WHITE, anchor="w").pack(fill="x")
        c_student_class = ttk.Combobox(left, values=self.__prof_classes, state="readonly")  # Selector de clase
        c_student_class.set(self.__prof_classes[-1] if len(self.__prof_classes) > 1 else "Sin clase")
        c_student_class.pack(fill="x", pady=(5, 14))

        right = tk.Frame(cols, bg=CARD, padx=18, pady=16)  # Panel derecho con la tabla de estudiantes
        right.grid(row=0, column=1, sticky="nsew")

        header_bar = tk.Frame(right, bg=CARD)
        header_bar.pack(fill="x")
        tk.Label(header_bar, text="Estudiantes en lista", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(side="left")
        self.app.make_button(
            header_bar, "Actualizar", self.refresh,
            color="#3b4658", padx=10, pady=4,
        ).pack(side="right")

        filter_bar = tk.Frame(right, bg=CARD)  # Barra superior de filtros por texto y por clase
        filter_bar.pack(fill="x", pady=(10, 12))

        search_row = tk.Frame(filter_bar, bg=FIELD, padx=10)
        search_row.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.app._draw_icon(search_row, "search", bg_color=FIELD, fg_color=MUTED).pack(side="left")
        search_ent = tk.Entry(search_row, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                              relief="flat", font=("Segoe UI", 10))
        search_ent.pack(side="left", fill="x", expand=True, ipady=7, padx=(8, 0))

        c_filter_class = ttk.Combobox(
            filter_bar,
            values=["Todas las clases"] + self.__prof_classes,
            state="readonly",
            width=18,
        )
        c_filter_class.set("Todas las clases")
        c_filter_class.pack(side="right", ipady=5)

        tree_wrap = tk.Frame(right, bg=FIELD)
        tree_wrap.pack(fill="both", expand=True)

        tree = ttk.Treeview(  # Tabla Treeview con 4 columnas: ID, Nombre, Clase y Rol
            tree_wrap,
            columns=("id", "nombre", "clase", "rol"),
            show="headings",
            style="Dark.Treeview",
            selectmode="browse",
        )
        tree.heading("id", text="ID", anchor="w")
        tree.heading("nombre", text="Nombre", anchor="w")
        tree.heading("clase", text="Clase", anchor="w")
        tree.heading("rol", text="Rol", anchor="w")
        tree.column("id", width=75, anchor="w")
        tree.column("nombre", width=165, anchor="w")
        tree.column("clase", width=125, anchor="w")
        tree.column("rol", width=85, anchor="w")
        tree.pack(side="left", fill="both", expand=True)

        # Funcion interna que rellena la tabla derecha aplicando los filtros activos
        def populate_students(filter_text=""):
            if not tree.winfo_exists():  # Verifica que la tabla siga activa
                return
            tree.delete(*tree.get_children())  # Limpia las filas existentes
            q = filter_text.lower()
            selected_cls = c_filter_class.get()
            for uid, uname, uclass, urole in self.__prof_users:  # Ciclo for que recorre la lista de estudiantes
                if selected_cls != "Todas las clases" and uclass != selected_cls:  # Filtra por clase seleccionada
                    continue
                if q in uid.lower() or q in uname.lower() or q in uclass.lower():  # Filtra por texto buscado
                    tree.insert("", "end", values=(uid, uname, uclass, urole))  # Inserta la fila en la tabla

        populate_students()  # Carga inicial de filas en la tabla
        search_ent.bind("<KeyRelease>", lambda e: populate_students(search_ent.get().strip()))
        c_filter_class.bind("<<ComboboxSelected>>", lambda e: populate_students(search_ent.get().strip()))

        # Funcion interna que copia los datos de la fila seleccionada al formulario izquierdo para editarlos
        def on_select_student_row(event=None):
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0], "values")  # Obtiene la tupla de valores de la fila
            if len(vals) >= 3:
                e_name.delete(0, "end")
                e_name.insert(0, str(vals[1]))
                if str(vals[0]) != "-":
                    e_id.delete(0, "end")
                    e_id.insert(0, str(vals[0]))
                if str(vals[2]) in self.__prof_classes:
                    c_student_class.set(str(vals[2]))

        tree.bind("<<TreeviewSelect>>", on_select_student_row)

        # Funcion interna que crea una nueva clase y actualiza los desplegables
        def create_class(event=None):
            cls_name = e_new_class.get().strip()
            if not cls_name:  # Valida que el nombre de la clase no este vacio
                messagebox.showwarning("Nombre vacío", "Escribe un nombre para la clase.")
                return
            for existing in self.__prof_classes:  # Ciclo for que verifica si la clase ya fue creada
                if existing.lower() == cls_name.lower():
                    messagebox.showinfo("Clase existente", f"La clase '{existing}' ya existe.")
                    c_student_class.set(existing)
                    return

            self.__prof_classes.append(cls_name)  # Agrega la nueva clase a la lista privada
            self._save_local_roster()  # Guarda en disco
            c_student_class.configure(values=self.__prof_classes)  # Actualiza selector de asignacion
            c_student_class.set(cls_name)  # Selecciona automaticamente la clase recien creada
            c_filter_class.configure(values=["Todas las clases"] + self.__prof_classes)  # Actualiza filtro derecho
            e_new_class.delete(0, "end")  # Limpia la caja de texto
            messagebox.showinfo("Clase creada", f"Clase '{cls_name}' creada correctamente.")

        e_new_class.bind("<Return>", create_class)  # Permite crear la clase presionando Enter
        self.app.make_button(class_row, "Crear", create_class, padx=12, pady=6).pack(side="right")

        add_student_btn = self.app.make_button(left, "Agregar estudiante", None)

        # Funcion interna que verifica el estudiante en el servidor y lo agrega a la clase elegida
        def add_existing_student(event=None):
            uname = e_name.get().strip()
            raw_uid = e_id.get().strip()
            chosen_class = c_student_class.get() or "Sin clase"

            if not uname or not raw_uid:  # Valida que nombre e ID esten completos
                messagebox.showwarning("Datos incompletos", "Ingresa el nombre y el ID del estudiante.")
                return
            if not raw_uid.isdigit() or len(raw_uid) > 10:  # Valida que el ID sea numerico positivo y maximo de 10 digitos
                messagebox.showwarning("ID inválido", "El ID debe contener solo números y tener máximo 10 dígitos.")
                return
            uid = int(raw_uid)  # Convierte el ID validado a numero entero

            add_student_btn.configure(state="disabled", text="Verificando...")

            def task():
                return self._verify_student_exists(uid, uname)  # Verifica contra el servidor

            def on_done(outcome):
                if add_student_btn.winfo_exists():
                    add_student_btn.configure(state="normal", text="Agregar estudiante")

                exists, msg = outcome  # Desempaqueta el booleano de resultado y el mensaje
                if not exists:  # Condicional si el estudiante no existe o el ID es incorrecto
                    messagebox.showerror("ID incorrecto o no existe", msg)
                    return

                uid_str = str(uid)
                self.__removed_students.discard(uid_str)  # Remueve el ID del conjunto de eliminados
                self.__removed_students.discard(uname.lower())  # Remueve el nombre del conjunto de eliminados

                updated = False  # Bandera para saber si se actualizo un registro existente
                for idx, (existing_id, existing_name, _, _) in enumerate(self.__prof_users):  # Busca coincidencia previa
                    if existing_id == uid_str or existing_name.strip().lower() == uname.lower():
                        self.__prof_users[idx] = (uid_str, uname, chosen_class, "Estudiante")  # Actualiza su clase
                        updated = True
                        break
                if not updated:  # Condicional si es un estudiante nuevo en la lista
                    self.__prof_users.append((uid_str, uname, chosen_class, "Estudiante"))  # Lo agrega al final

                self._save_local_roster()  # Guarda los cambios en el archivo JSON
                if e_name.winfo_exists():
                    e_name.delete(0, "end")
                if e_id.winfo_exists():
                    e_id.delete(0, "end")
                populate_students(search_ent.get().strip() if search_ent.winfo_exists() else "")
                messagebox.showinfo(
                    "Estudiante agregado",
                    f"{uname} (ID: {uid_str}) fue añadido a la clase '{chosen_class}'.",
                )

            def on_err(err):
                if add_student_btn.winfo_exists():
                    add_student_btn.configure(state="normal", text="Agregar estudiante")
                messagebox.showerror("Error de conexión", str(err))

            self.app._run_async(task, on_done, on_err)

        # Funcion interna que elimina al estudiante seleccionado de la lista del profesor
        def remove_selected_student(event=None):
            sel = tree.selection()
            if not sel:  # Condicional si no hay ninguna fila seleccionada
                messagebox.showinfo("Selecciona uno", "Haz clic en un estudiante de la tabla para eliminarlo.")
                return
            values = tree.item(sel[0], "values")
            uid_str, uname = str(values[0]), str(values[1])

            if not messagebox.askyesno(  # Solicita confirmacion antes de eliminar
                "Eliminar estudiante",
                f"¿Deseas eliminar a {uname} (ID: {uid_str}) de tu lista?",
            ):
                return

            self.__prof_users = [  # Reconstruye la lista excluyendo al estudiante eliminado
                u for u in self.__prof_users
                if not (u[0] == uid_str and u[1] == uname)
            ]
            if uid_str != "-":  # Registra el ID en el conjunto de eliminados para que no reaparezca al sincronizar
                self.__removed_students.add(uid_str)
            self.__removed_students.add(uname.lower())
            self._save_local_roster()  # Persiste la eliminacion en disco
            populate_students(search_ent.get().strip())  # Actualiza la tabla en pantalla

        e_id.bind("<Return>", add_existing_student)  # Permite agregar presionando Enter en el campo ID
        tree.bind("<Delete>", remove_selected_student)  # Permite eliminar presionando la tecla Suprimir

        add_student_btn.configure(command=add_existing_student)
        add_student_btn.pack(fill="x", pady=(4, 0))
        self.app.make_button(
            right, "Eliminar estudiante seleccionado", remove_selected_student,
            color="#b91c1c", pady=8,
        ).pack(fill="x", pady=(10, 0))

    # Funcion que muestra la tarjeta de perfil con los datos de sesion del profesor
    def _render_prof_profile(self, body):
        tk.Label(body, text="Perfil", bg=BG, fg=WHITE,
                 font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x", pady=(0, 14))
        card = tk.Frame(body, bg=CARD, padx=22, pady=20)
        card.pack(fill="x")
        tk.Label(card, text=f"Usuario ID: {self.app.user_id}", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=4)
        tk.Label(card, text="Rol: Profesor", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=4)
        tk.Label(card, text=f"Servidor conectado: {URL}", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=4)


# =============================================================================
# CLASE 2: INTERFAZ DEL ESTUDIANTE (Con visor esquemático interactivo PySpice)
# =============================================================================

# Clase encargada de gestionar el panel del estudiante, la descarga de practicas y la simulacion SPICE
class StudentView(BasePanel):

    # Metodo constructor que inicializa los atributos privados del estudiante y el simulador interactivo
    def __init__(self, parent, app, initial_labs_raw=None):
        super().__init__(parent, app)  # Llama al constructor de BasePanel
        self.__initial_labs_raw = initial_labs_raw  # Guarda la lista inicial de practicas recibida en el login
        self.__labs_tree = None  # Inicializa en None la referencia a la tabla de practicas asignadas
        self.__notebook = None  # Inicializa en None el contenedor de pestanas Notebook
        self.__sim_lab_name = None  # Inicializa en None la entrada de texto con el nombre del ZIP
        self.__sim_console = None  # Inicializa en None el widget Text de la consola de resultados
        self.__schematic_canvas = None  # Inicializa en None el lienzo Canvas del esquema electrico
        self.__comp_tree = None  # Inicializa en None la tabla de componentes editables
        self.__current_cir_path = None  # Inicializa en None la ruta del archivo .cir descomprimido
        self.__current_netlist_lines = []  # Inicializa vacia la lista de lineas del netlist SPICE activo
        self.__parsed_components = []  # Inicializa vacia la lista de diccionarios de componentes detectados
        self.__node_voltages = {}  # Inicializa vacio el diccionario {nombre_nodo: voltaje_calculado}

    # Funcion que construye la interfaz completa del estudiante con barra superior y pestanas
    def render(self):
        self.app.title(f"Virtual Lab - Panel del estudiante (ID: {self.app.user_id})")  # Actualiza titulo de ventana

        header = tk.Frame(self, bg=CARD, padx=18, pady=12)  # Crea la barra superior oscura
        header.pack(fill="x")
        tk.Label(header, text="VIRTUAL LAB", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Label(header, text=f"ID {self.app.user_id} · Estudiante · {URL}",
                 bg=CARD, fg=MUTED).pack(side="left", padx=20)
        self.app.make_button(header, "Cerrar sesión", self.app.logout,
                             color="#3b4658", pady=7).pack(side="right")

        self.__notebook = ttk.Notebook(self)  # Crea el widget de pestanas ttk.Notebook
        self.__notebook.pack(fill="both", expand=True, padx=20, pady=(14, 18))
        self.student_tabs(self.__notebook)  # Construye las pestanas interiores

    # Implementacion polimorfica que actualiza la lista de practicas asignadas desde el servidor
    def refresh(self):
        try:
            raw = client.listStudentLabs(URL, self.app.user_id)  # Llama al cliente para listar practicas del alumno
            self._populate_student_labs(raw)  # Actualiza las filas de la tabla
        except Exception as exc:  # Captura errores de conexion con el servidor
            self.write_console(f"[Aviso] No se pudieron cargar las prácticas: {exc}")

    # Funcion auxiliar que crea un marco contenedor y lo registra como pestana en el Notebook
    def make_tab(self, notebook, name):
        frame = tk.Frame(notebook, bg=BG, padx=16, pady=16)  # Crea el marco de la pestana
        notebook.add(frame, text=name)  # Agrega el marco al Notebook con su titulo
        return frame  # Retorna el marco creado

    # Funcion que construye las pestanas "Prácticas asignadas" y "Simulación" del estudiante
    def student_tabs(self, tabs):
        view = self.make_tab(tabs, "Prácticas asignadas")  # Crea la primera pestana
        top_bar = tk.Frame(view, bg=BG)  # Barra superior con instrucciones y boton de actualizacion
        top_bar.pack(fill="x", pady=(0, 10))
        tk.Label(top_bar, text="Selecciona una práctica asignada para descargarla o abrirla en el simulador:",
                 bg=BG, fg=MUTED).pack(side="left")
        self.app.make_button(top_bar, "Actualizar lista", self.refresh,
                             color="#3b4658", pady=7).pack(side="right")

        columns = ("practica", "profesor", "estado")  # Tupla con los identificadores de columna de la tabla
        self.__labs_tree = ttk.Treeview(view, columns=columns, show="headings", height=9)  # Crea la tabla de practicas
        self.__labs_tree.heading("practica", text="Práctica (.zip)")  # Configura encabezado 1
        self.__labs_tree.heading("profesor", text="Asignado por (ID Prof.)")  # Configura encabezado 2
        self.__labs_tree.heading("estado", text="Estado")  # Configura encabezado 3
        self.__labs_tree.column("practica", width=380, anchor="w")  # Configura ancho y alineacion de columna 1
        self.__labs_tree.column("profesor", width=200, anchor="center")  # Configura ancho y alineacion de columna 2
        self.__labs_tree.column("estado", width=220, anchor="center")  # Configura ancho y alineacion de columna 3
        self.__labs_tree.pack(fill="both", expand=True, pady=(0, 12))
        self.__labs_tree.bind("<<TreeviewSelect>>", self.on_select_lab)  # Enlaza el evento de seleccion de fila

        btn_bar = tk.Frame(view, bg=BG)  # Barra inferior con botones de descarga y simulacion
        btn_bar.pack(fill="x")
        self.app.make_button(btn_bar, "Descargar práctica seleccionada",
                             self.download_selected_lab).pack(side="left", padx=(0, 10))
        self.app.make_button(btn_bar, "Simular práctica seleccionada",
                             self.go_to_simulation_tab, color=GREEN).pack(side="left")

        sim = self.make_tab(tabs, "Simulación")  # Crea la segunda pestana ("Simulación")

        ctrl_bar = tk.Frame(sim, bg=CARD, padx=14, pady=10)  # Barra superior de controles del simulador
        ctrl_bar.pack(fill="x", pady=(0, 10))

        tk.Label(ctrl_bar, text="Archivo ZIP:", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self.__sim_lab_name = tk.Entry(ctrl_bar, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                                       relief="flat", font=("Segoe UI", 10), width=26)  # Campo con el nombre del ZIP
        self.__sim_lab_name.pack(side="left", ipady=6, padx=(0, 10))

        self.app.make_button(ctrl_bar, "▶ Simular circuito",
                             self.run_simulation, color=GREEN, padx=12, pady=6).pack(side="left", padx=(0, 8))
        self.app.make_button(ctrl_bar, "↺ Restaurar original",
                             self.reset_original_netlist, color="#3b4658", padx=10, pady=6).pack(side="left", padx=(0, 8))
        self.app.make_button(ctrl_bar, "Abrir carpeta",
                             self.open_labs_folder, color="#3b4658", padx=10, pady=6).pack(side="right")

        workspace = tk.Frame(sim, bg=BG)  # Area de trabajo dividida en esquema (izquierda) y tabla/consola (derecha)
        workspace.pack(fill="both", expand=True)
        workspace.columnconfigure(0, weight=6)  # Columna izquierda con 60% del ancho
        workspace.columnconfigure(1, weight=4)  # Columna derecha con 40% del ancho
        workspace.rowconfigure(0, weight=1)

        left_panel = tk.Frame(workspace, bg=CARD, padx=12, pady=12)  # Tarjeta izquierda del visor esquematico
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        schem_hdr = tk.Frame(left_panel, bg=CARD)  # Cabecera del visor esquematico
        schem_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(schem_hdr, text="Esquema del circuito simulado", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(schem_hdr, text="Haz clic sobre un componente para editar su valor",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(side="right")

        self.__schematic_canvas = tk.Canvas(left_panel, bg=FIELD, highlightthickness=1,
                                            highlightbackground="#2b3a52", cursor="hand2")  # Lienzo de dibujo electrico
        self.__schematic_canvas.pack(fill="both", expand=True)
        self.__schematic_canvas.bind("<Configure>", lambda e: self._draw_circuit_schematic())  # Redibuja al cambiar tamano

        right_panel = tk.Frame(workspace, bg=BG)  # Contenedor derecho dividido en 2 filas verticales
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=5)  # Fila superior (50% alto) para tabla de componentes
        right_panel.rowconfigure(1, weight=5)  # Fila inferior (50% alto) para consola de resultados
        right_panel.columnconfigure(0, weight=1)

        comp_card = tk.Frame(right_panel, bg=CARD, padx=12, pady=10)  # Tarjeta superior de componentes editables
        comp_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        comp_hdr = tk.Frame(comp_card, bg=CARD)
        comp_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(comp_hdr, text="Componentes (doble clic para cambiar valor)", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        self.app.make_button(comp_hdr, "Editar valor", self.edit_selected_component,
                             color=BLUE, padx=8, pady=3).pack(side="right")

        self.__comp_tree = ttk.Treeview(  # Tabla Treeview de componentes SPICE
            comp_card,
            columns=("comp", "nodos", "valor"),
            show="headings",
            style="Dark.Treeview",
            height=5,
        )
        self.__comp_tree.heading("comp", text="Elemento", anchor="w")
        self.__comp_tree.heading("nodos", text="Nodos", anchor="w")
        self.__comp_tree.heading("valor", text="Valor", anchor="w")
        self.__comp_tree.column("comp", width=85, anchor="w")
        self.__comp_tree.column("nodos", width=105, anchor="w")
        self.__comp_tree.column("valor", width=95, anchor="w")
        self.__comp_tree.pack(fill="both", expand=True)
        self.__comp_tree.bind("<Double-1>", lambda e: self.edit_selected_component())  # Abre editor con doble clic

        console_card = tk.Frame(right_panel, bg=CARD, padx=12, pady=10)  # Tarjeta inferior de consola de resultados
        console_card.grid(row=1, column=0, sticky="nsew")
        tk.Label(console_card, text="Resultados de simulación (Punto de Operación DC)", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", pady=(0, 6))

        self.__sim_console = tk.Text(console_card, bg=FIELD, fg="#4ade80", relief="flat",
                                     height=7, font=("Consolas", 9), state="disabled")  # Consola verde de solo lectura
        self.__sim_console.pack(fill="both", expand=True)

        self._draw_empty_schematic()  # Dibuja el estado inicial vacio en el Canvas
        self.write_console("Listo. Descarga una práctica asignada y presiona '▶ Simular circuito'.")

        if self.__initial_labs_raw is not None:  # Condicional si ya se recibieron practicas al iniciar sesion
            self._populate_student_labs(self.__initial_labs_raw)  # Rellena la tabla sin repetir consulta
        else:  # Caso contrario si no se pasaron datos iniciales
            self.refresh()  # Consulta al servidor

    # Funcion que rellena la tabla del estudiante verificando si cada .zip ya fue descargado en disco
    def _populate_student_labs(self, raw):
        for item in self.__labs_tree.get_children():  # Ciclo for que elimina las filas previas de la tabla
            self.__labs_tree.delete(item)
        if not raw or str(raw).strip().lower() == "error":  # Condicional que sale si la respuesta es vacia o error
            return

        if isinstance(raw, str):  # Condicional que decodifica la respuesta si viene como cadena
            text = raw.strip()
            try:
                labs = json.loads(text)  # Intenta convertir JSON a lista
            except Exception:
                try:
                    labs = ast.literal_eval(text)  # Intenta evaluar lista de Python
                except Exception:
                    labs = [line.strip() for line in text.splitlines() if line.strip()]  # Separa por lineas
        else:  # Caso contrario si raw ya es una lista
            labs = raw

        if not isinstance(labs, list):  # Condicional de seguridad para verificar que labs sea una lista
            return

        for entry in labs:  # Ciclo for que recorre cada practica asignada al estudiante
            if isinstance(entry, dict):  # Condicional si cada elemento viene como diccionario
                lab_name = entry.get("lab_name", "desconocido.zip")
                prof_id = entry.get("professor_id", "Profesor")
            else:  # Caso contrario si viene como cadena con el nombre de la practica
                lab_name = str(entry)
                prof_id = "Asignado"
            zip_name = lab_name if lab_name.lower().endswith(".zip") else f"{lab_name}.zip"  # Asegura extension .zip
            local_file = os.path.join("client", "labs", zip_name)  # Construye la ruta local esperada
            if os.path.exists(local_file) and zipfile.is_zipfile(local_file):  # Verifica existencia fisica y validez ZIP
                estado = "Descargado"
            else:  # Caso contrario si aun no ha sido descargado
                estado = "Disponible en servidor"
            self.__labs_tree.insert("", tk.END, values=(zip_name, prof_id, estado))  # Inserta la fila en la tabla

    # Funcion que autocompleta el nombre del archivo .zip en la pestana Simulacion al elegir una fila
    def on_select_lab(self, event=None):
        selected = self.__labs_tree.selection()  # Obtiene la seleccion actual de la tabla
        if not selected:  # Condicional que sale si no hay seleccion
            return
        lab_name = self.__labs_tree.item(selected[0], "values")[0]  # Extrae el nombre del ZIP de la fila
        self.__sim_lab_name.delete(0, tk.END)  # Limpia la caja de texto del simulador
        self.__sim_lab_name.insert(0, lab_name)  # Inserta el nombre de la practica seleccionada

    # Funcion que cambia a la pestana Simulacion y ejecuta la practica seleccionada
    def go_to_simulation_tab(self):
        self.on_select_lab()  # Copia el nombre de la practica seleccionada al campo de simulacion
        self.__notebook.select(1)  # Cambia el foco a la pestana de indice 1 ("Simulación")
        if self.__sim_lab_name.get().strip():  # Condicional que ejecuta la simulacion si hay un nombre cargado
            self.run_simulation()

    # Funcion que descarga desde el servidor el archivo .zip de la practica seleccionada
    def download_selected_lab(self):
        selected = self.__labs_tree.selection()  # Obtiene la fila seleccionada en la tabla
        if not selected:  # Condicional que advierte si no se eligio ninguna practica
            messagebox.showwarning("Selección", "Selecciona una práctica de la tabla primero.")
            return
        name = self.__labs_tree.item(selected[0], "values")[0].strip()  # Obtiene el nombre del archivo
        if not name.lower().endswith(".zip"):  # Condicional para asegurar extension .zip
            name += ".zip"
        self.__sim_lab_name.delete(0, tk.END)  # Actualiza el campo de simulacion con el nombre descargado
        self.__sim_lab_name.insert(0, name)

        os.makedirs("client/labs", exist_ok=True)  # Crea la carpeta local client/labs si no existe
        target_path = os.path.join("client", "labs", name)  # Construye la ruta de destino del archivo
        try:
            res = client.downloadLab(URL, self.app.user_id, name)  # Descarga los bytes del laboratorio desde el servidor
            if os.path.exists(target_path) and not zipfile.is_zipfile(target_path):  # Valida que el archivo sea un ZIP real
                with open(target_path, "r", encoding="utf-8", errors="ignore") as f:  # Lee el mensaje de error guardado
                    err_content = f.read().strip()
                os.remove(target_path)  # Borra el archivo invalido
                messagebox.showerror(
                    "Error de descarga",
                    f"El servidor rechazó la descarga de '{name}' ({err_content or '404'}).\n"
                    "Verifica que la práctica exista y esté asignada a tu usuario."
                )
                return
            messagebox.showinfo("Descarga", str(res))  # Muestra confirmacion de descarga
            if res is not None:  # Condicional que actualiza la tabla si la descarga fue exitosa
                self.refresh()
        except Exception as exc:  # Captura errores de red o disco
            messagebox.showerror("Error", f"Descarga\n\n{exc}")

    # Funcion que escribe mensajes en la consola verde del simulador
    def write_console(self, text, clear=False):
        self.__sim_console.config(state="normal")  # Habilita la escritura en el widget Text
        if clear:  # Condicional que borra el contenido anterior si clear es True
            self.__sim_console.delete("1.0", tk.END)
        self.__sim_console.insert(tk.END, text + "\n")  # Agrega la nueva linea de texto al final
        self.__sim_console.see(tk.END)  # Desplaza la barra de desplazamiento hasta el final
        self.__sim_console.config(state="disabled")  # Vuelve a bloquear el widget para evitar edicion manual

    # Funcion que analiza las lineas del netlist SPICE para extraer componentes editables (R, V, I, C, L, D)
    def _parse_spice_components(self, lines):
        components = []  # Inicializa una lista vacia para los componentes detectados
        for idx, line in enumerate(lines):  # Ciclo for que recorre cada linea junto con su indice
            stripped = line.strip()  # Elimina espacios al inicio y al final de la linea
            if not stripped or stripped.startswith(("*", ".", "+")):  # Condicional que omite comentarios y directivas SPICE
                continue  # Salta a la siguiente linea
            tokens = stripped.split()  # Divide la linea en palabras separadas por espacios
            if len(tokens) < 4:  # Condicional que omite lineas incompletas
                continue
            name = tokens[0]  # Primer token: nombre del componente (ej. R1, V1)
            prefix = name[0].upper()  # Primera letra en mayuscula que identifica el tipo de elemento
            if prefix in ("R", "V", "I", "C", "L"):  # Condicional para resistencias, fuentes, capacitores e inductores
                n1, n2, val = tokens[1], tokens[2], tokens[3]  # Extrae nodo positivo, nodo negativo y valor
                components.append({  # Agrega un diccionario con los metadatos del componente
                    "line_idx": idx,
                    "name": name,
                    "type": prefix,
                    "n1": n1,
                    "n2": n2,
                    "value": val,
                    "extra": " ".join(tokens[4:]),
                })
            elif prefix == "D":  # Condicional para diodos
                n1, n2, model = tokens[1], tokens[2], tokens[3]  # Extrae anodo, catodo y modelo SPICE
                components.append({  # Agrega el diccionario del diodo
                    "line_idx": idx,
                    "name": name,
                    "type": prefix,
                    "n1": n1,
                    "n2": n2,
                    "value": model,
                    "extra": " ".join(tokens[4:]),
                })
        return components  # Retorna la lista de componentes extraidos

    # Funcion que actualiza las filas de la tabla derecha de componentes
    def _refresh_components_table(self):
        for item in self.__comp_tree.get_children():  # Ciclo for que elimina las filas anteriores
            self.__comp_tree.delete(item)
        for comp in self.__parsed_components:  # Ciclo for que inserta cada componente con su valor actual
            nodos_txt = f"{comp['n1']} → {comp['n2']}"  # Formatea los nodos conectados
            self.__comp_tree.insert("", tk.END, values=(comp["name"], nodos_txt, comp["value"]))

    # Funcion que abre un cuadro de dialogo para editar el valor de un componente y re-simula al instante
    def edit_selected_component(self, comp_index=None):
        if not self.__parsed_components:  # Condicional que verifica si hay un circuito cargado
            messagebox.showinfo("Sin circuito", "Simula primero un archivo ZIP para editar sus componentes.")
            return

        if comp_index is None:  # Condicional cuando se invoca desde la tabla y no desde el Canvas
            sel = self.__comp_tree.selection()  # Obtiene la fila seleccionada en la tabla
            if not sel:  # Advierte si no hay ningun componente seleccionado
                messagebox.showinfo("Selecciona un elemento", "Haz doble clic en un componente de la tabla o en el esquema.")
                return
            comp_index = self.__comp_tree.index(sel[0])  # Obtiene el indice numerico de la fila

        if comp_index < 0 or comp_index >= len(self.__parsed_components):  # Condicional de seguridad de rango
            return

        comp = self.__parsed_components[comp_index]  # Recupera el diccionario del componente elegido
        new_val = simpledialog.askstring(  # Abre cuadro de dialogo para pedir el nuevo valor
            f"Editar {comp['name']}",
            f"Componente: {comp['name']} (Nodos {comp['n1']} → {comp['n2']})\n"
            f"Valor actual: {comp['value']}\n\n"
            "Ingresa el nuevo valor (ej. 5k, 12, 470, 10u):",
            initialvalue=comp["value"],
            parent=self,
        )
        if new_val is None or not new_val.strip():  # Condicional si el usuario cancelo o dejo vacio el campo
            return

        clean_val = new_val.strip().split()[0]  # Toma el primer token limpio sin espacios
        comp["value"] = clean_val  # Actualiza el valor en el diccionario del componente
        extra_str = f" {comp['extra']}" if comp["extra"] else ""  # Conserva parametros adicionales si existen
        self.__current_netlist_lines[comp["line_idx"]] = f"{comp['name']} {comp['n1']} {comp['n2']} {clean_val}{extra_str}"

        self._refresh_components_table()  # Refresca la tabla de componentes
        self._execute_loaded_netlist(source_label=f"{os.path.basename(self.__current_cir_path)} (modificado)")  # Re-simula

    # Funcion que restaura el archivo .cir original desde el paquete .zip y vuelve a simular
    def reset_original_netlist(self):
        self.__current_cir_path = None  # Limpia la ruta en memoria
        self.__current_netlist_lines = []  # Limpia las lineas modificadas
        self.run_simulation()  # Vuelve a extraer y simular el paquete original

    # Funcion que dibuja el mensaje de bienvenida en el Canvas cuando aun no se ha simulado ningun circuito
    def _draw_empty_schematic(self):
        if self.__schematic_canvas is None or not self.__schematic_canvas.winfo_exists():  # Verifica existencia del Canvas
            return
        c = self.__schematic_canvas  # Alias corto para el Canvas
        c.delete("all")  # Limpia todos los elementos previos
        w = c.winfo_width() or 520  # Obtiene el ancho actual o usa 520 por defecto
        h = c.winfo_height() or 380  # Obtiene el alto actual o usa 380 por defecto
        c.create_text(
            w // 2, h // 2 - 10,
            text="⚡ Visor esquemático interactivo",
            fill=WHITE, font=("Segoe UI", 12, "bold")
        )
        c.create_text(
            w // 2, h // 2 + 16,
            text="Ejecuta una simulación para visualizar el circuito, sus voltajes nodales y editar componentes",
            fill=MUTED, font=("Segoe UI", 9), width=w - 60, justify="center"
        )

    # Funcion que dibuja automaticamente el esquema electrico del circuito simulado y sus voltajes nodales
    def _draw_circuit_schematic(self):
        if self.__schematic_canvas is None or not self.__schematic_canvas.winfo_exists():  # Verifica existencia del Canvas
            return
        c = self.__schematic_canvas
        c.delete("all")  # Borra dibujos anteriores

        if not self.__parsed_components:  # Condicional si no hay componentes cargados
            self._draw_empty_schematic()  # Muestra la pantalla de espera
            return

        w = max(460, c.winfo_width())  # Garantiza un ancho minimo de dibujo de 460 px
        h = max(340, c.winfo_height())  # Garantiza un alto minimo de dibujo de 340 px

        ordered_nodes = []  # Lista ordenada de nodos activos distintos de tierra
        for comp in self.__parsed_components:  # Ciclo for que recorre cada componente
            for n in (comp["n1"], comp["n2"]):  # Ciclo for que inspecciona ambos terminales del componente
                if n.lower() not in ("0", "gnd") and n not in ordered_nodes:  # Excluye tierra y evita duplicados
                    ordered_nodes.append(n)  # Agrega el nodo a la lista ordenada

        if not ordered_nodes:  # Condicional de respaldo si todos los nodos fueran tierra
            ordered_nodes = ["1"]

        margin_x = 85  # Margen horizontal izquierdo y derecho en pixeles
        top_y = 85  # Coordenada Y donde se ubican los nodos superiores
        gnd_y = h - 70  # Coordenada Y donde se dibuja la linea inferior de tierra
        mid_y = (top_y + gnd_y) // 2  # Coordenada Y intermedia para componentes verticales

        node_x = {}  # Diccionario que almacenara la coordenada X de cada nodo
        if len(ordered_nodes) == 1:  # Condicional cuando existe un unico nodo activo
            node_x[ordered_nodes[0]] = w // 2  # Ubica el nodo en el centro horizontal
        else:  # Caso contrario cuando hay dos o mas nodos activos
            step = (w - 2 * margin_x) / (len(ordered_nodes) - 1)  # Calcula la separacion horizontal uniforme
            for i, n in enumerate(ordered_nodes):  # Ciclo for que asigna coordenada X a cada nodo
                node_x[n] = int(margin_x + i * step)

        left_bus = min(node_x.values()) - 25  # Extremo izquierdo del bus de tierra
        right_bus = max(node_x.values()) + 25  # Extremo derecho del bus de tierra
        c.create_line(left_bus, gnd_y, right_bus, gnd_y, fill=CYAN, width=2)  # Dibuja linea horizontal de tierra
        gx = (left_bus + right_bus) // 2  # Centro horizontal para el simbolo de tierra
        c.create_line(gx, gnd_y, gx, gnd_y + 12, fill=CYAN, width=2)  # Vastago vertical de tierra
        c.create_line(gx - 14, gnd_y + 12, gx + 14, gnd_y + 12, fill=CYAN, width=2)  # Primera barra de tierra
        c.create_line(gx - 9, gnd_y + 17, gx + 9, gnd_y + 17, fill=CYAN, width=2)  # Segunda barra de tierra
        c.create_line(gx - 4, gnd_y + 22, gx + 4, gnd_y + 22, fill=CYAN, width=2)  # Tercera barra de tierra
        c.create_text(gx + 34, gnd_y + 14, text="GND (0 V)", fill=MUTED, font=("Consolas", 8, "bold"))  # Etiqueta GND

        for n, nx in node_x.items():  # Ciclo for que dibuja cada nodo superior y su voltaje calculado
            c.create_oval(nx - 5, top_y - 5, nx + 5, top_y + 5, fill=AMBER, outline=WHITE, width=1)  # Punto del nodo
            v_val = self._lookup_node_voltage(n)  # Consulta el voltaje calculado para este nodo
            v_txt = f" ({v_val:.3f} V)" if v_val is not None else ""  # Formatea el voltaje con 3 decimales
            c.create_text(nx, top_y - 22, text=f"Nodo {n}{v_txt}",
                          fill=AMBER, font=("Consolas", 9, "bold"))  # Etiqueta ambar sobre el nodo

        horiz_offset = 0  # Desplazamiento vertical acumulativo para ramas horizontales en paralelo
        for idx, comp in enumerate(self.__parsed_components):  # Ciclo for que dibuja cada componente del circuito
            n1, n2 = comp["n1"], comp["n2"]
            n1_gnd = n1.lower() in ("0", "gnd")  # Evalua si el terminal 1 esta conectado a tierra
            n2_gnd = n2.lower() in ("0", "gnd")  # Evalua si el terminal 2 esta conectado a tierra
            tag = f"comp_{idx}"  # Etiqueta unica que identifica graficamente al componente

            if not n1_gnd and not n2_gnd:  # Condicional cuando el componente conecta dos nodos distintos de tierra
                x1, x2 = node_x[n1], node_x[n2]
                y = top_y + horiz_offset
                if horiz_offset > 0:  # Dibuja bajantes verticales si hay componentes en paralelo
                    c.create_line(x1, top_y, x1, y, fill=CYAN, width=2, tags=tag)
                    c.create_line(x2, top_y, x2, y, fill=CYAN, width=2, tags=tag)
                self._draw_horizontal_symbol(c, x1, x2, y, comp, tag)  # Dibuja el simbolo horizontal
                horiz_offset += 38  # Incrementa el desplazamiento para el siguiente componente horizontal
            else:  # Caso contrario cuando uno de los terminales va a tierra
                active_node = n2 if n1_gnd else n1  # Identifica el nodo superior activo
                x = node_x[active_node]
                self._draw_vertical_symbol(c, x, top_y, gnd_y, mid_y, comp, n1_gnd, tag)  # Dibuja el simbolo vertical

            c.tag_bind(tag, "<Button-1>", lambda e, i=idx: self.edit_selected_component(i))  # Enlaza clic al editor

    # Funcion auxiliar que busca el voltaje de un nodo ignorando diferencias de mayusculas
    def _lookup_node_voltage(self, node_name):
        target = node_name.strip().lower()  # Normaliza el nombre buscado a minusculas
        for k, v in self.__node_voltages.items():  # Ciclo for que recorre los voltajes calculados
            if k.strip().lower() == target:  # Condicional si coincide el nombre del nodo
                return v  # Retorna el valor numerico del voltaje
        return None  # Retorna None si no se encontro el nodo

    # Funcion que dibuja un simbolo electrico horizontal entre x1 y x2 en el Canvas
    def _draw_horizontal_symbol(self, c, x1, x2, y, comp, tag):
        if x1 > x2:  # Condicional que asegura que x1 sea siempre la coordenada izquierda
            x1, x2 = x2, x1
        mx = (x1 + x2) // 2  # Calcula el punto medio horizontal
        c.create_line(x1, y, mx - 24, y, fill=CYAN, width=2, tags=tag)  # Terminal conductor izquierdo
        c.create_line(mx + 24, y, x2, y, fill=CYAN, width=2, tags=tag)  # Terminal conductor derecho
        c.create_rectangle(mx - 28, y - 24, mx + 28, y + 22, fill="", outline="", tags=tag)  # Zona transparente clicable

        if comp["type"] == "R":  # Condicional para dibujar el zigzag de una resistencia
            pts = [mx - 24, y, mx - 18, y - 8, mx - 10, y + 8, mx - 2, y - 8,
                   mx + 6, y + 8, mx + 14, y - 8, mx + 20, y + 8, mx + 24, y]
            c.create_line(*pts, fill=WHITE, width=2, tags=tag)
        elif comp["type"] == "C":  # Condicional para dibujar las dos placas paralelas de un capacitor
            c.create_line(mx - 5, y - 12, mx - 5, y + 12, fill=WHITE, width=2.5, tags=tag)
            c.create_line(mx + 5, y - 12, mx + 5, y + 12, fill=WHITE, width=2.5, tags=tag)
            c.create_line(mx - 24, y, mx - 5, y, fill=CYAN, width=2, tags=tag)
            c.create_line(mx + 5, y, mx + 24, y, fill=CYAN, width=2, tags=tag)
        else:  # Caso por defecto para otros elementos (inductor, diodo, fuente)
            c.create_rectangle(mx - 22, y - 10, mx + 22, y + 10, fill=CARD, outline=WHITE, width=2, tags=tag)

        c.create_text(mx, y - 19, text=f"{comp['name']} = {comp['value']}",
                      fill=WHITE, font=("Consolas", 9, "bold"), tags=tag)  # Etiqueta con nombre y valor

    # Funcion que dibuja un simbolo electrico vertical entre top_y y gnd_y en el Canvas
    def _draw_vertical_symbol(self, c, x, top_y, gnd_y, mid_y, comp, inverted, tag):
        c.create_line(x, top_y, x, mid_y - 24, fill=CYAN, width=2, tags=tag)  # Conductor superior
        c.create_line(x, mid_y + 24, x, gnd_y, fill=CYAN, width=2, tags=tag)  # Conductor inferior hacia tierra
        c.create_rectangle(x - 35, mid_y - 26, x + 35, mid_y + 26, fill="", outline="", tags=tag)  # Zona clicable

        if comp["type"] in ("V", "I"):  # Condicional para dibujar el circulo de una fuente de voltaje o corriente
            c.create_oval(x - 20, mid_y - 20, x + 20, mid_y + 20, fill=CARD, outline=GREEN, width=2, tags=tag)
            top_sign = "-" if inverted else "+"  # Determina el signo superior segun la polaridad
            bot_sign = "+" if inverted else "-"  # Determina el signo inferior segun la polaridad
            c.create_text(x, mid_y - 8, text=top_sign, fill=GREEN, font=("Consolas", 10, "bold"), tags=tag)
            c.create_text(x, mid_y + 9, text=bot_sign, fill=WHITE, font=("Consolas", 10, "bold"), tags=tag)
        elif comp["type"] == "R":  # Condicional para dibujar zigzag vertical de resistencia
            pts = [x, mid_y - 24, x - 8, mid_y - 18, x + 8, mid_y - 10, x - 8, mid_y - 2,
                   x + 8, mid_y + 6, x - 8, mid_y + 14, x + 8, mid_y + 20, x, mid_y + 24]
            c.create_line(*pts, fill=WHITE, width=2, tags=tag)
        elif comp["type"] == "C":  # Condicional para dibujar placas horizontales de capacitor vertical
            c.create_line(x - 13, mid_y - 5, x + 13, mid_y - 5, fill=WHITE, width=2.5, tags=tag)
            c.create_line(x - 13, mid_y + 5, x + 13, mid_y + 5, fill=WHITE, width=2.5, tags=tag)
            c.create_line(x, mid_y - 24, x, mid_y - 5, fill=CYAN, width=2, tags=tag)
            c.create_line(x, mid_y + 5, x, mid_y + 24, fill=CYAN, width=2, tags=tag)
        else:  # Caso por defecto para otros elementos
            c.create_rectangle(x - 11, mid_y - 20, x + 11, mid_y + 20, fill=CARD, outline=WHITE, width=2, tags=tag)

        c.create_text(x + 28, mid_y - 7, text=comp["name"], anchor="w",
                      fill=WHITE, font=("Consolas", 9, "bold"), tags=tag)  # Nombre del componente a la derecha
        c.create_text(x + 28, mid_y + 8, text=comp["value"], anchor="w",
                      fill=CYAN, font=("Consolas", 9), tags=tag)  # Valor del componente debajo del nombre

    # Funcion que extrae el archivo .cir del paquete .zip descargado y dispara la simulacion SPICE
    def run_simulation(self):
        name = self.__sim_lab_name.get().strip()  # Obtiene el nombre del archivo ingresado
        if not name:  # Condicional que advierte si el campo esta vacio
            messagebox.showwarning("Archivo", "Selecciona o escribe el nombre del ZIP a simular.")
            return
        zip_name = name if name.endswith(".zip") else f"{name}.zip"  # Agrega extension .zip si falta
        zip_path = os.path.join("client", "labs", zip_name)  # Ruta esperada dentro de client/labs
        if not os.path.exists(zip_path):  # Si no esta en client/labs, busca en el directorio actual
            zip_path = zip_name
        if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):  # Verifica existencia y validez del ZIP
            messagebox.showwarning("Archivo no encontrado", "Descarga primero un archivo ZIP válido antes de simular.")
            return

        try:
            extract_dir = os.path.join("client", "labs")
            os.makedirs(extract_dir, exist_ok=True)
            cir_file = None  # Variable para guardar la ruta del archivo .cir encontrado
            with zipfile.ZipFile(zip_path, "r") as zf:  # Abre el archivo ZIP en modo lectura
                zf.extractall(extract_dir)  # Extrae todos los archivos contenidos en client/labs
                for member in zf.namelist():  # Ciclo for que recorre los nombres de archivo dentro del ZIP
                    if member.endswith(".cir"):  # Condicional que detecta el archivo de circuito SPICE
                        cir_file = os.path.join(extract_dir, member)
                        break  # Detiene la busqueda al encontrar el primer .cir

            if not cir_file or not os.path.exists(cir_file):  # Condicional si el paquete ZIP no contenia ningun .cir
                messagebox.showerror("Práctica inválida", "El ZIP no contiene ningún archivo .cir.")
                return

            with open(cir_file, "r", encoding="utf-8-sig") as f:  # Abre el .cir eliminando marca BOM si existe
                raw_lines = [line.rstrip() for line in f.readlines()]  # Lee todas las lineas quitando saltos finales

            while raw_lines and not raw_lines[0].strip():  # Ciclo while que elimina lineas vacias al inicio
                raw_lines.pop(0)

            if raw_lines:  # Condicional para asegurar que la primera linea sea un titulo valido en SPICE
                first_line = raw_lines[0].strip()
                first_token = first_line.split()[0].upper()
                if first_line.startswith("*"):  # Si empieza con comentario '*', lo convierte en titulo
                    raw_lines[0] = first_line.lstrip("*").strip() or f"Circuito {os.path.basename(cir_file)}"
                elif first_token.startswith(".") or re.match(r"^[VIRCLDQMXEFGH][0-9_]", first_token):
                    raw_lines.insert(0, f"Circuito {os.path.basename(cir_file)}")  # Inserta una linea de titulo arriba

            self.__current_cir_path = cir_file  # Guarda la ruta del .cir activo
            self.__current_netlist_lines = raw_lines  # Guarda las lineas editables del netlist
            self.__parsed_components = self._parse_spice_components(raw_lines)  # Extrae los componentes del netlist
            self._refresh_components_table()  # Llena la tabla derecha de componentes
            self._execute_loaded_netlist(source_label=zip_name)  # Ejecuta la simulacion con PySpice
        except Exception as exc:  # Captura cualquier excepcion durante la extraccion o lectura
            self.write_console(f"[Error de simulación] {exc}")
            messagebox.showerror("Simulación", f"No se pudo ejecutar PySpice:\n\n{exc}")

    # Funcion que ejecuta PySpice/ngspice sobre el netlist en memoria y actualiza resultados y esquema
    def _execute_loaded_netlist(self, source_label=""):
        if not self.__current_netlist_lines:  # Condicional que sale si no hay lineas cargadas
            return
        try:
            netlist = "\n".join(self.__current_netlist_lines)  # Une todas las lineas en una sola cadena SPICE
            self.write_console(f"Simulando: {source_label}...", clear=True)
            self.write_console("--- Netlist activo ---")
            self.write_console(netlist)
            self.write_console("----------------------")

            from PySpice.Spice.Parser import SpiceParser  # Importa SpiceParser para analizar el netlist
            parser = SpiceParser(source=netlist)  # Instancia el analizador con el netlist activo
            circuit = parser.build_circuit()  # Construye el objeto Circuit de PySpice
            if not getattr(circuit, "title", None):  # Asigna un titulo si el circuito no lo tiene
                circuit.title = f"Circuito {source_label}"

            simulator = circuit.simulator(temperature=25, nominal_temperature=25)  # Crea el simulador ngspice a 25 °C
            resultados = []  # Lista vacia para almacenar tuplas (nombre_nodo, voltaje)

            try:
                analysis = simulator.operating_point()  # Ejecuta el analisis de punto de operacion DC
                for node_name, node in analysis.nodes.items():  # Ciclo for que recorre cada nodo calculado
                    resultados.append((str(node_name), float(node[0])))  # Guarda el nombre y voltaje del nodo
            except Exception as sim_err:  # Respaldo directo sobre ngspice si falla el wrapper asincrono
                ngspice_obj = getattr(simulator, "ngspice", None)
                if ngspice_obj is not None:
                    if hasattr(ngspice_obj, "clear_output"):
                        ngspice_obj.clear_output()  # Limpia la salida previa de ngspice
                    ngspice_obj.exec_command("op")  # Ejecuta el comando SPICE 'op'
                    ngspice_obj.exec_command("print all")  # Imprime todos los voltajes nodales en stdout
                    salida = getattr(ngspice_obj, "stdout", "") or ""
                    for match in re.finditer(  # Ciclo for que extrae pares nodo = voltaje con expresion regular
                        r"^\s*(?:v\(([^)]+)\)|([a-zA-Z_][\w.#]*))\s*=\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)",
                        salida,
                        flags=re.IGNORECASE | re.MULTILINE,
                    ):
                        nombre = (match.group(1) or match.group(2)).strip()
                        valor = float(match.group(3))
                        if "#branch" not in nombre.lower():  # Omite corrientes de rama y conserva solo voltajes
                            resultados.append((nombre, valor))

                if not resultados:  # Condicional si tampoco se obtuvieron resultados por consola
                    detalle = (getattr(ngspice_obj, "stderr", "") or getattr(ngspice_obj, "stdout", "")) if ngspice_obj else ""
                    if detalle:
                        self.write_console(f"[Detalle ngspice] {detalle.strip()}")
                    raise sim_err  # Relanza la excepcion original

            self.__node_voltages = {nombre: voltaje for nombre, voltaje in resultados}  # Diccionario de voltajes nodales
            self.write_console("Análisis de punto de operación (OP):")
            for node_name, voltage in resultados:  # Ciclo for que imprime cada voltaje nodal en la consola
                self.write_console(f"  Node {node_name}: {voltage:.4f} V")
            self.write_console("Simulación completada. Haz clic en un componente para modificarlo.")
            self._draw_circuit_schematic()  # Redibuja el esquema electrico con los nuevos voltajes
        except Exception as exc:  # Captura errores de sintaxis SPICE o ejecucion de ngspice
            self.write_console(f"[Error de simulación] {exc}")
            messagebox.showerror("Simulación", f"No se pudo ejecutar PySpice:\n\n{exc}")

    # Funcion que abre la carpeta local client/labs en el explorador de archivos del sistema operativo
    def open_labs_folder(self):
        folder = os.path.abspath("client/labs")  # Obtiene la ruta absoluta de client/labs
        os.makedirs(folder, exist_ok=True)  # Crea la carpeta si aun no existe
        try:
            if sys.platform.startswith("win"):  # Condicional para sistemas Windows
                os.startfile(folder)  # Abre el Explorador de Windows
            elif sys.platform == "darwin":  # Condicional para sistemas macOS
                subprocess.Popen(["open", folder])  # Abre Finder
            else:  # Caso contrario para sistemas Linux
                subprocess.Popen(["xdg-open", folder])  # Abre el gestor de archivos predeterminado
        except Exception as e:
            messagebox.showerror("Carpeta", str(e))


# =============================================================================
# CLASE PRINCIPAL: CONTROLADOR DE SESIÓN Y FÁBRICA DE COMPONENTES VISUALES
# =============================================================================

# Ventana principal de la aplicacion grafica Virtual Lab
class VirtualLab(tk.Tk):

    # Metodo constructor que inicializa la ventana raiz, estilos oscuros, variables privadas y login
    def __init__(self):
        super().__init__()  # Llama al constructor de tk.Tk para crear la ventana principal
        self.title("Virtual Lab")  # Establece el titulo inicial de la ventana
        self.geometry("1060x680")  # Establece el tamano inicial de 1060x680 pixeles
        self.minsize(880, 580)  # Define el tamano minimo permitido de 880x580 pixeles
        self.configure(bg=BG)  # Aplica el color de fondo oscuro principal

        self._setup_styles()  # Configura los temas visuales oscuros para ttk
        self._load_saved_url()  # Carga la ultima URL del servidor desde archivo local

        self.__user_id = None  # Atributo privado que almacena el ID del usuario autenticado
        self.__role = None  # Atributo privado que almacena el rol ("professor" o "student")
        self.__session = None  # Atributo privado que guarda la respuesta de sesion del servidor
        self.__session_active = False  # Bandera booleana privada que indica si hay sesion activa
        self.__active_panel = None  # Referencia privada al panel hijo actualmente visible

        self.container = tk.Frame(self, bg=BG)  # Crea el marco contenedor principal donde cambian las pantallas
        self.container.pack(fill="both", expand=True)  # Expande el contenedor a toda la ventana

        self.show_login()  # Despliega la vista inicial de inicio de sesion
        self.update_idletasks()  # Procesa las tareas pendientes de geometria de Tkinter

    # Propiedad de solo lectura que retorna el ID del usuario conectado
    @property
    def user_id(self):
        return self.__user_id  # Retorna el atributo privado __user_id

    # Propiedad de solo lectura que retorna el rol del usuario conectado
    @property
    def role(self):
        return self.__role  # Retorna el atributo privado __role

    # Propiedad de solo lectura que retorna si la sesion esta activa
    @property
    def session_active(self):
        return self.__session_active  # Retorna el atributo privado __session_active

    # Funcion que guarda de forma controlada los datos de la sesion iniciada
    def set_session(self, user_id, role, session_data):
        self.__user_id = user_id  # Asigna el ID del usuario
        self.__role = role  # Asigna el rol detectado
        self.__session = session_data  # Guarda los datos de sesion
        self.__session_active = True  # Marca la sesion como activa

    # Funcion que monta y renderiza polimorficamente cualquier subclase de BasePanel
    def show_panel(self, panel: BasePanel):
        self.clear_screen(keep=panel)  # Destruye pantallas anteriores conservando el nuevo panel
        self.__active_panel = panel  # Guarda la referencia al panel activo
        try:
            panel.pack(fill="both", expand=True)  # Empaqueta el panel ocupando toda la ventana
            panel.render()  # Invoca el metodo render() propio de ProfessorView o StudentView
            self.update_idletasks()  # Actualiza el dibujado de los widgets
        except Exception as exc:  # Captura cualquier fallo al construir el panel
            messagebox.showerror("Error al cargar interfaz", f"No se pudo cargar el panel:\n\n{exc}")
            self.show_login()  # Regresa al inicio de sesion en caso de error

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN DE RED, ESTILOS Y MÉTODOS AUXILIARES COMPARTIDOS
    # -------------------------------------------------------------------------

    # Funcion que lee desde disco la ultima URL del servidor guardada
    def _load_saved_url(self):
        global URL  # Indica que se modificara la variable global URL
        if not os.path.exists(SERVER_CONFIG_FILE):  # Condicional que sale si no existe el archivo JSON
            return
        try:
            with open(SERVER_CONFIG_FILE, "r", encoding="utf-8") as f:  # Abre el archivo JSON en modo lectura
                data = json.load(f)  # Carga el diccionario JSON
            saved = str(data.get("url", "")).strip()  # Obtiene y limpia el valor de la clave "url"
            if saved:  # Condicional que actualiza URL si la cadena no esta vacia
                URL = saved
        except Exception:
            pass

    # Funcion que normaliza el formato de la URL ingresada y la guarda en client/server_config.json
    def _apply_server_url(self, raw_url):
        global URL  # Indica que se modificara la variable global URL
        text = (raw_url or "").strip().rstrip("/")  # Limpia espacios y barras diagonales finales
        if not text:  # Condicional que asigna localhost si el usuario dejo el campo vacio
            text = "http://127.0.0.1:80"
        if not text.startswith(("http://", "https://")):  # Condicional que agrega http:// si no tiene protocolo
            text = f"http://{text}"
        host_part = text.split("://", 1)[1]  # Extrae la parte posterior a http://
        if ":" not in host_part and "/" not in host_part:  # Condicional que agrega puerto :80 si no se especifico puerto
            text = f"{text}:80"

        URL = text  # Actualiza la variable global URL
        try:
            os.makedirs("client", exist_ok=True)  # Crea la carpeta client si no existe
            with open(SERVER_CONFIG_FILE, "w", encoding="utf-8") as f:  # Abre el JSON en modo escritura
                json.dump({"url": URL}, f, indent=2)  # Guarda la URL normalizada
        except Exception:
            pass
        return URL  # Retorna la URL final

    # Funcion que configura los estilos oscuros de ttk para pestanas y tablas Treeview
    def _setup_styles(self):
        style = ttk.Style(self)  # Crea el objeto gestor de estilos ttk
        style.theme_use("clam")  # Selecciona el tema base "clam" para personalizar colores

        style.configure("TNotebook", background=BG, borderwidth=0)  # Estilo del contenedor de pestanas
        style.configure(
            "TNotebook.Tab",
            background=CARD,
            foreground=MUTED,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )  # Estilo de las pestanas inactivas
        style.map(
            "TNotebook.Tab",
            background=[("selected", BLUE)],
            foreground=[("selected", WHITE)],
        )  # Estilo de la pestana seleccionada

        style.configure(
            "Treeview",
            background=FIELD,
            foreground=WHITE,
            fieldbackground=FIELD,
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10),
        )  # Estilo general de tablas Treeview
        style.configure(
            "Treeview.Heading",
            background="#263449",
            foreground=WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )  # Estilo de encabezados de tabla
        style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", WHITE)])  # Fila seleccionada

        style.configure(
            "Dark.Treeview",
            background=FIELD,
            foreground=WHITE,
            fieldbackground=FIELD,
            borderwidth=0,
            rowheight=30,
            font=("Segoe UI", 9),
        )  # Estilo oscuro compacto para tablas del panel docente y simulador
        style.map(
            "Dark.Treeview",
            background=[("selected", BLUE)],
            foreground=[("selected", WHITE)],
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#162032",
            foreground=WHITE,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Dark.Treeview.Heading", background=[("active", "#1e2c44")])

    # Funcion que ejecuta una tarea de red en un hilo secundario y agenda los callbacks en Tkinter
    def _run_async(self, task, on_success, on_error=None):
        # Funcion interna ejecutada por el hilo secundario
        def worker():
            try:
                result = task()  # Ejecuta la llamada de red bloqueante
                if self.winfo_exists():  # Verifica que la ventana principal siga abierta
                    self.after(0, lambda: on_success(result))  # Ejecuta on_success en el hilo principal
            except Exception as exc:  # Captura errores de red o excepciones inesperadas
                if self.winfo_exists():
                    if on_error:  # Condicional si se proporciono un manejador de error personalizado
                        self.after(0, lambda: on_error(exc))
                    else:  # Caso contrario muestra un cuadro de dialogo estandar
                        self.after(0, lambda: messagebox.showerror("Error de conexión", str(exc)))

        threading.Thread(target=worker, daemon=True).start()  # Crea e inicia el hilo daemon

    # Funcion que elimina los widgets hijos de self.container excepto el indicado en keep
    def clear_screen(self, keep=None):
        for widget in self.container.winfo_children():  # Ciclo for que recorre todos los widgets dentro de container
            if keep is not None and widget is keep:  # Condicional para conservar el widget especificado
                continue
            widget.destroy()  # Destruye el widget anterior

    # Funcion fabrica que crea y retorna un boton plano estilizado
    def make_button(self, parent, text, command, color=BLUE, padx=12, pady=10):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=BLUE_HOVER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=padx,
            pady=pady,
        )

    # Funcion fabrica que crea una etiqueta acompaniada de su campo de entrada tk.Entry
    def add_field(self, parent, label, secret=False):
        tk.Label(parent, text=label, bg=parent.cget("bg"), fg=WHITE, anchor="w").pack(fill="x")  # Crea etiqueta
        entry = tk.Entry(
            parent,
            show="*" if secret else "",  # Oculta el texto con asteriscos si secret es True
            bg=FIELD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", ipady=8, pady=(5, 12))  # Posiciona la caja de texto
        return entry  # Retorna la referencia del widget Entry

    # Metodo estatico que valida en tiempo real que un campo de ID solo reciba digitos y maximo 10 caracteres
    @staticmethod
    def _validate_id_input(new_value):
        return new_value == "" or (new_value.isdigit() and len(new_value) <= 10)  # Permite vacio o hasta 10 digitos

    # Funcion auxiliar que ejecuta una llamada al cliente HTTP mostrando el resultado o el error
    def safe_call(self, title, function, *args):
        try:
            result = function(*args)  # Invoca la funcion pasando los argumentos variables
            messagebox.showinfo(title, str(result))  # Muestra la respuesta en una alerta
            return result
        except Exception as exc:  # Captura cualquier excepcion durante la llamada
            messagebox.showerror("Error", f"{title}\n\n{exc}")
            return None

    # Funcion que dibuja iconos vectoriales en Canvas segun el identificador kind
    def _draw_icon(self, parent, kind, bg_color, fg_color=WHITE, size=18):
        c = tk.Canvas(parent, width=size, height=size, bg=bg_color, highlightthickness=0)  # Crea lienzo cuadrado
        s = size / 20.0  # Calcula el factor de escala respecto a una cuadricula de 20x20
        w = 1.6  # Grosor de trazo

        if kind == "home":  # Condicional para dibujar icono de inicio (casa)
            c.create_polygon(3 * s, 9.5 * s, 10 * s, 3 * s, 17 * s, 9.5 * s,
                             fill="", outline=fg_color, width=w)  # Techo triangular
            c.create_line(5 * s, 9 * s, 5 * s, 17 * s, 15 * s, 17 * s, 15 * s, 9 * s,
                          fill=fg_color, width=w)  # Paredes y piso
        elif kind == "doc":  # Condicional para dibujar icono de documento
            c.create_polygon(5 * s, 2.5 * s, 12.5 * s, 2.5 * s, 15.5 * s, 5.5 * s,
                             15.5 * s, 17.5 * s, 5 * s, 17.5 * s,
                             fill="", outline=fg_color, width=w)  # Contorno de hoja
            c.create_line(7.5 * s, 9 * s, 13 * s, 9 * s, fill=fg_color, width=w)  # Renglon superior
            c.create_line(7.5 * s, 12.5 * s, 13 * s, 12.5 * s, fill=fg_color, width=w)  # Renglon inferior
        elif kind == "users":  # Condicional para dibujar icono de grupo de usuarios
            c.create_oval(4.5 * s, 4 * s, 10.5 * s, 10 * s, outline=fg_color, width=w)  # Cabeza principal
            c.create_arc(2 * s, 11.5 * s, 13 * s, 20 * s, start=0, extent=180,
                         style="arc", outline=fg_color, width=w)  # Hombros principales
            c.create_oval(11 * s, 5 * s, 16 * s, 10 * s, outline=fg_color, width=w)  # Cabeza secundaria
            c.create_arc(10.5 * s, 12 * s, 18.5 * s, 19.5 * s, start=0, extent=150,
                         style="arc", outline=fg_color, width=w)  # Hombros secundarios
        elif kind == "user":  # Condicional para dibujar icono de perfil individual
            c.create_oval(6.5 * s, 3 * s, 13.5 * s, 10 * s, outline=fg_color, width=w)  # Cabeza
            c.create_arc(3.5 * s, 11.5 * s, 16.5 * s, 21 * s, start=0, extent=180,
                         style="arc", outline=fg_color, width=w)  # Hombros
        elif kind == "search":  # Condicional para dibujar icono de lupa
            c.create_oval(3.5 * s, 3.5 * s, 13.5 * s, 13.5 * s, outline=fg_color, width=w)  # Lente circular
            c.create_line(12.5 * s, 12.5 * s, 17 * s, 17 * s, fill=fg_color, width=w)  # Mango de la lupa
        return c  # Retorna el widget Canvas con el icono dibujado

    # -------------------------------------------------------------------------
    # VENTANA DE INICIO DE SESIÓN Y REGISTRO
    # -------------------------------------------------------------------------

    # Funcion que construye la pantalla de inicio de sesion centrada
    def show_login(self):
        self.clear_screen()  # Limpia cualquier vista anterior
        self.title("Virtual Lab - Inicio de sesión")  # Actualiza el titulo de la ventana

        wrapper = tk.Frame(self.container, bg=BG)  # Marco envolvente para centrar la tarjeta
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(wrapper, bg=CARD, padx=36, pady=24)  # Tarjeta oscura central del formulario
        card.pack(expand=True)
        tk.Frame(card, bg=CARD, width=328, height=1).pack()  # Regla invisible para fijar ancho minimo

        tk.Label(card, text="⚗  VIRTUAL LAB", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 14))
        tk.Label(card, text="Iniciar sesión", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 15, "bold")).pack()
        tk.Label(card, text="Acceso al sistema", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(pady=(2, 14))

        tk.Label(card, text="Servidor (IP local o 127.0.0.1)", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x")
        self.server_entry = tk.Entry(card, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                                     relief="flat", font=("Segoe UI", 10))  # Campo para IP o URL del servidor
        self.server_entry.insert(0, URL)  # Rellena el campo con la URL guardada
        self.server_entry.pack(fill="x", ipady=7, pady=(4, 11))

        tk.Label(card, text="ID de usuario", bg=CARD, fg=WHITE, anchor="w").pack(fill="x")
        vcmd_id = (tk.Misc.register(self, self._validate_id_input), "%P")  # Usa el registro interno de Tkinter (max 10 digitos)
        self.id_entry = tk.Entry(card, bg=FIELD, fg=WHITE, insertbackground=WHITE,
                                 relief="flat", font=("Segoe UI", 11),
                                 validate="key", validatecommand=vcmd_id)  # Campo para el ID numerico (max 10 digitos)
        self.id_entry.pack(fill="x", ipady=8, pady=(5, 11))

        tk.Label(card, text="Contraseña", bg=CARD, fg=WHITE, anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(card, show="*", bg=FIELD, fg=WHITE,
                                       insertbackground=WHITE, relief="flat",
                                       font=("Segoe UI", 11))  # Campo oculto para la contrasena
        self.password_entry.pack(fill="x", ipady=8, pady=(5, 16))

        self.login_btn = self.make_button(card, "Iniciar sesión", self.login)  # Boton de autenticacion
        self.login_btn.pack(fill="x")

        tk.Label(card, text="¿No tienes cuenta?", bg=CARD, fg=MUTED).pack(pady=(14, 6))
        self.make_button(card, "Registrar nuevo usuario", self.open_register_from_login,
                         color="#3b4658").pack(fill="x")  # Boton para ir a registro

        self.id_entry.focus_set()  # Enfoca el cursor en el campo ID
        self.password_entry.bind("<Return>", lambda event: self.login())  # Permite iniciar sesion con Enter

    # Funcion que guarda la URL escrita antes de abrir la pantalla de registro
    def open_register_from_login(self):
        if hasattr(self, "server_entry") and self.server_entry.winfo_exists():  # Verifica si existe el campo servidor
            self._apply_server_url(self.server_entry.get())  # Guarda la URL ingresada
        self.show_register()  # Navega al formulario de registro

    # Funcion que valida credenciales, identifica el rol y carga el panel correspondiente
    def login(self):
        server_url = self._apply_server_url(self.server_entry.get())  # Normaliza y guarda la URL del servidor
        if self.server_entry.winfo_exists():
            self.server_entry.delete(0, "end")
            self.server_entry.insert(0, server_url)

        raw_id = self.id_entry.get().strip()  # Obtiene el ID ingresado
        password = self.password_entry.get()  # Obtiene la contrasena ingresada

        if not raw_id or not password:  # Condicional que valida campos obligatorios
            messagebox.showwarning("Datos incompletos", "Ingresa tu ID y contraseña.")
            return

        if not raw_id.isdigit() or len(raw_id) > 10:  # Valida que el ID contenga solo numeros y maximo 10 digitos
            messagebox.showwarning("ID inválido", "El ID debe contener solo números y tener máximo 10 dígitos.")
            return

        user_id = int(raw_id)  # Convierte el ID validado a entero

        self.login_btn.configure(state="disabled", text="Verificando...")

        # Funcion interna que ejecuta la autenticacion y deteccion de rol en segundo plano
        def task():
            resp = client.openSession(server_url, user_id, password)  # Abre sesion en el servidor
            if not resp or any(w in str(resp).lower() for w in ("error", "incorrect", "invalid", "failed", "denied")):
                return ("auth_error", resp, None)  # Retorna error si el servidor rechazo las credenciales

            explicit_role = self.detect_role(resp)  # Comprueba si la respuesta incluye el rol
            if explicit_role != "student":  # Si no viene marcado como estudiante, prueba si es profesor
                labs_raw = client.listProfessorsLabs(server_url, user_id)  # Consulta laboratorios de profesor
                if "error" not in str(labs_raw).lower():  # Si el servidor lo autoriza, su rol es profesor
                    return ("professor", resp, labs_raw)

            student_labs_raw = client.listStudentLabs(server_url, user_id)  # Consulta practicas del estudiante
            return ("student", resp, student_labs_raw)  # Retorna rol estudiante con sus practicas

        # Funcion interna que despliega el panel correspondiente tras autenticar
        def on_done(outcome):
            status, resp, data_primary = outcome  # Desempaqueta estado, respuesta y datos iniciales
            if self.login_btn.winfo_exists():
                self.login_btn.configure(state="normal", text="Iniciar sesión")

            if status == "auth_error":  # Condicional si las credenciales fueron rechazadas
                messagebox.showerror("Acceso denegado", "ID o contraseña incorrectos.")
                return

            self.set_session(user_id, status, resp)  # Almacena los datos de sesion en la instancia VirtualLab

            if status == "professor":  # Condicional para instanciar la vista de profesor
                panel = ProfessorView(self.container, self, initial_labs_raw=data_primary)
            else:  # Caso contrario para instanciar la vista de estudiante
                panel = StudentView(self.container, self, initial_labs_raw=data_primary)
            self.show_panel(panel)  # Muestra el panel seleccionado polimorficamente

        def on_err(error):
            if self.login_btn.winfo_exists():
                self.login_btn.configure(state="normal", text="Iniciar sesión")
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar con {server_url}.\n\n{error}\n\n"
                "Verifica que el servidor esté encendido y que ambos equipos estén en la misma red."
            )

        self._run_async(task, on_done, on_err)

    # Metodo estatico que extrae el rol si la respuesta del login viene como diccionario
    @staticmethod
    def detect_role(response):
        if isinstance(response, dict):  # Condicional que comprueba si la respuesta es un diccionario
            role = response.get("role") or response.get("user", {}).get("role")  # Busca la clave role
            if isinstance(role, str):  # Condicional si el valor es texto
                role = role.lower()
                if role in ("professor", "profesor"):  # Retorna "professor" si coincide
                    return "professor"
                if role in ("student", "estudiante"):  # Retorna "student" si coincide
                    return "student"
        return None  # Retorna None si no se pudo determinar el rol desde el diccionario

    # Funcion que construye la pantalla de registro de nuevos usuarios
    def show_register(self):
        self.clear_screen()  # Limpia la vista anterior
        self.title("Virtual Lab - Registro de usuario")

        wrapper = tk.Frame(self.container, bg=BG)
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(wrapper, bg=CARD, padx=35, pady=24)  # Tarjeta oscura central
        card.pack(expand=True)
        tk.Frame(card, bg=CARD, width=360, height=1).pack()

        tk.Label(card, text="⚗  VIRTUAL LAB", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 17, "bold")).pack(pady=(0, 8))
        tk.Label(card, text="Crear cuenta", bg=CARD, fg=WHITE,
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(card, text=f"Servidor: {URL}",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(3, 14))

        self.reg_name = self.add_field(card, "Nombre completo")  # Campo para el nombre del nuevo usuario
        self.reg_id = self.add_field(card, "ID de usuario (máx. 10 dígitos)")  # Campo para el ID numerico
        vcmd_id = (tk.Misc.register(self, self._validate_id_input), "%P")  # Usa el registro interno de Tkinter (max 10 digitos)
        self.reg_id.configure(validate="key", validatecommand=vcmd_id)  # Bloquea letras o mas de 10 digitos al escribir

        tk.Label(card, text="Rol", bg=CARD, fg=WHITE, anchor="w").pack(fill="x")
        self.reg_role = ttk.Combobox(card, values=["Estudiante", "Profesor"], state="readonly")  # Selector de rol
        self.reg_role.set("Estudiante")  # Selecciona "Estudiante" por defecto
        self.reg_role.pack(fill="x", pady=(5, 12))

        self.reg_password = self.add_field(card, "Contraseña", secret=True)  # Campo oculto para contrasena

        self.reg_btn = self.make_button(card, "Registrarse", self.register)  # Boton de envio de registro
        self.reg_btn.pack(fill="x", pady=(5, 8))
        self.make_button(card, "Volver al inicio de sesión",
                         self.show_login, color="#3b4658").pack(fill="x")  # Boton para regresar al login

    # Funcion que valida los campos y envia la solicitud de registro al servidor
    def register(self):
        name = self.reg_name.get().strip()  # Obtiene el nombre completo
        raw_id = self.reg_id.get().strip()  # Obtiene el ID ingresado
        role_es = self.reg_role.get()  # Obtiene el rol seleccionado en espanol
        role_backend = "professor" if role_es == "Profesor" else "student"  # Traduce el rol al formato esperado por el servidor
        password = self.reg_password.get()  # Obtiene la contrasena

        if not all([name, raw_id, role_es, password]):  # Condicional que comprueba que ningun campo este vacio
            messagebox.showwarning("Datos incompletos", "Completa todos los campos.")
            return
        if not raw_id.isdigit() or len(raw_id) > 10:  # Valida que el ID contenga solo numeros y maximo 10 digitos
            messagebox.showwarning("ID inválido", "El ID debe contener solo números y tener máximo 10 dígitos.")
            return
        user_id = int(raw_id)  # Convierte el ID validado a entero

        self.reg_btn.configure(state="disabled", text="Registrando...")

        def task():
            return client.registerUser(URL, name, user_id, role_backend, password)  # Envia los datos al servidor

        def on_done(response):
            if self.reg_btn.winfo_exists():
                self.reg_btn.configure(state="normal", text="Registrarse")

            if "already registered" in str(response).lower():  # Condicional si el ID ya existe en el servidor
                messagebox.showwarning("ID duplicado", f"El ID {user_id} ya se encuentra registrado.")
                return
            if "error" in str(response).lower():  # Condicional si el servidor reporto otro error
                messagebox.showerror("Error de registro", f"No se pudo registrar:\n{response}")
                return

            messagebox.showinfo("Registro exitoso", f"Usuario {name} registrado como {role_es}.")
            self.show_login()  # Regresa al inicio de sesion tras completar el registro

        def on_err(error):
            if self.reg_btn.winfo_exists():
                self.reg_btn.configure(state="normal", text="Registrarse")
            messagebox.showerror("Error de registro", str(error))

        self._run_async(task, on_done, on_err)

    # Funcion que cierra la sesion en el servidor en segundo plano y vuelve al inicio de sesion
    def logout(self):
        uid = self.__user_id  # Guarda localmente el ID antes de limpiar los atributos
        active = self.__session_active  # Guarda el estado de sesion activa
        current_url = URL  # Guarda la URL actual del servidor

        self.__user_id = None  # Reinicia el atributo privado __user_id
        self.__role = None  # Reinicia el atributo privado __role
        self.__session = None  # Reinicia el atributo privado __session
        self.__session_active = False  # Marca la sesion como inactiva
        self.__active_panel = None  # Limpia la referencia al panel activo

        self.show_login()  # Muestra de inmediato la pantalla de inicio de sesion

        if uid is not None and active:  # Condicional que cierra la sesion en el servidor en hilo secundario
            threading.Thread(
                target=lambda: client.closeSession(current_url, uid),
                daemon=True,
            ).start()


if __name__ == "__main__":  # Condicional que verifica si el archivo se ejecuta como programa principal
    app = VirtualLab()  # Crea la instancia de la ventana principal VirtualLab
    app.mainloop()  # Inicia el ciclo infinito de eventos graficos de Tkinter
