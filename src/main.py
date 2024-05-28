"""Main controller"""

import sqlite3
import subprocess
from datetime import datetime
from tkinter import Label, Frame, Entry, Tk, filedialog
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.constants import END, PRIMARY, INFO, YES, BOTH, SUCCESS
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from openpyxl import Workbook
import ttkbootstrap as ttk


class Main:
    """Main program"""

    def __init__(self, window_app, db_app):
        self.wind = window_app
        self.db_name = db_app
        self.grado_selected_id = 0
        self.alumno_selected_id = 0
        self.nombre_alumno_selected = None
        self.main_frame = None

        # Ventana minizada: Ancho y alto de la pantalla a la mitad
        width = self.wind.winfo_screenwidth() / 2
        height = self.wind.winfo_screenheight() / 2
        self.wind.geometry(f"{int(width)}x{int(height)}")

        # Ventanta maximizada: Full
        self.wind.state("zoomed")

        self.wind.title("Sistema de asistencias")
        self.set_principal_view()

    def reset_view(self):
        """Eliminar todos los widgets de la vista actual"""
        # Eliminar widgets de la vista principal
        for widget in self.wind.winfo_children():
            widget.destroy()

        # Quitar el escuchador de eventos "Enter" de la ventana principal
        self.wind.unbind("<Return>")

    def reset_input_codigo(self, event):
        """Ctrl + BackSpace -> Borrar todo el contenido del input"""
        print(event)
        self.input_codigo.delete(0, END)

    def run_query(self, query, parameters=()):
        """Ejecutar cualquier query y obtener el resultado"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
        return result

    def display_success_toast(self, message):
        """Notificación para cuando una operación se realice con éxito"""
        toast = ToastNotification(
            title="Operación exitosa", message=message, duration=2000, icon=None
        )
        toast.show_toast()

    def display_error_box(self, message, parent=None):
        """Mostrar un Messagebox centrado"""
        if parent is None:
            parent = self.main_frame

        Messagebox.show_error(message=message, title="Advertencia", parent=parent)
        # overlay.destroy()

    def set_change_view_link_corner(self, content, on_click):
        """Colocar link button en la esquina superior derecha"""
        # Botón "Ver reporte" posicionado en la esquina superior derecha
        boton_reporte = ttk.Button(
            self.wind, text=content, bootstyle=INFO, command=on_click
        )
        boton_reporte.place(relx=1.0, y=25, x=-30, anchor="ne")

    def register_asistencia(self, codigo_alumno):
        """Función para registrar asistencia cuando se presione 'Enter' en la vista principal"""
        if codigo_alumno in (None, ""):
            return self.display_error_box("Código inválido")

        result = self.run_query(
            "SELECT alumno_id, nombres, apellidos FROM alumnos WHERE codigo = ?",
            [codigo_alumno],
        )
        alumno = result.fetchone()

        if alumno in (None, "") or len(alumno) == 0:
            return self.display_error_box("No se encontró el alumno")

        fecha_actual = datetime.now().isoformat()
        asistencia = self.run_query(
            "INSERT INTO asistencias(alumno_id, llegada) VALUES (?, ?)",
            [alumno[0], fecha_actual],
        )

        if asistencia:
            return self.display_success_toast(
                f"Asistencia marcada para el alumno: {alumno[1]} {alumno[2]}"
            )

        return self.display_error_box("Error interno al registrar asistencia")

    def set_principal_view(self):
        """Mostrar vista principal"""
        self.reset_view()

        # Frame Container
        self.main_frame = ttk.Frame(self.wind, borderwidth=0, relief="flat")
        self.main_frame.pack(expand=True)

        # Hero principal
        main_titulo = Label(
            self.main_frame,
            text="Esperando código de barras...",
            font=("Sans-serif", 22),
        )
        main_titulo.pack(expand=True)

        # Frame para el input y el botón
        frame_input_boton = Frame(self.main_frame)
        frame_input_boton.pack(expand=True)

        # Input código de barras
        self.input_codigo = Entry(
            frame_input_boton, font=("Helvetica", 18), justify="center"
        )
        self.input_codigo.pack(side="left")
        self.input_codigo.focus()

        # Evento Ctrl + Delete
        self.input_codigo.bind("<Control-BackSpace>", self.reset_input_codigo)

        # Botón "agregar manualmente"
        boton_agregar = ttk.Button(
            frame_input_boton,
            text="Agregar manualmente",
            bootstyle=PRIMARY,
            command=lambda: self.register_asistencia(self.input_codigo.get()),
        )
        boton_agregar.pack(side="left", padx=10, pady=20)

        # Escuchador de evento "Enter" a la ventana principal
        self.wind.bind(
            "<Return>", lambda event: self.register_asistencia(self.input_codigo.get())
        )

        # Botón "Ver reporte" posicionado en la esquina superior derecha
        boton_reporte = ttk.Button(
            self.wind,
            text="Ver reporte",
            bootstyle=INFO,
            command=self.set_reporte_view,
        )
        boton_reporte.place(relx=1.0, y=25, x=-30, anchor="ne")

    def set_reporte_view(self):
        """Mostrar segunda vista con todos los grados disponibles"""
        self.reset_view()
        # Frame Container
        self.main_frame = ttk.Frame(self.wind, borderwidth=0, relief="flat", padding=20)
        self.main_frame.pack(expand=True)

        # Titulo
        main_titulo = ttk.Label(
            self.main_frame,
            text="GRADOS DISPONIBLES",
            font=("Sans-serif", 24),
            padding=(0, 30),
        )
        main_titulo.pack(expand=True)

        self.set_change_view_link_corner("Marcar asistencias", self.set_principal_view)

        # Grados registrados en la base de datos
        grados = self.run_query(
            """
            SELECT g.grado_id, g.grado, n.nivel FROM grados g
            INNER JOIN niveles n ON g.nivel_id = n.nivel_id
            """
        ).fetchall()

        # Contenedor para los grados
        grados_frame = ttk.Frame(self.main_frame)
        grados_frame.pack(expand=True)

        # Configurar variables para el "flex-wrap"
        max_botones_por_fila = 3
        fila_actual = ttk.Frame(grados_frame)
        fila_actual.pack(side="top", pady=5)
        contador_botones_en_fila = 0

        # Crear un estilo personalizado
        estilo = ttk.Style()

        # Configurar el tamaño de la fuente para el estilo del botón
        estilo.configure(
            "BotonGrado.TButton", font=("sans-serif", 11), width=30, justify="center"
        )

        # Agregar cada botón a la UI
        for grado in grados:
            grado_button = ttk.Button(
                fila_actual,
                text=f"{grado[0]}. {(grado[1]).capitalize()} de {grado[2]}",
                style="BotonGrado.TButton",
                command=lambda grado=grado[
                    0
                ], nombre=f"{grado[1].capitalize()} de {grado[2]}": self.set_alumnos_view(
                    grado, nombre
                ),
            )
            grado_button.pack(side="left", padx=5, pady=5)

            contador_botones_en_fila += 1

            # Verificar si se debe envolver a la siguiente fila
            if contador_botones_en_fila >= max_botones_por_fila:
                fila_actual = ttk.Frame(grados_frame)
                fila_actual.pack(side="top", pady=5)
                contador_botones_en_fila = 0

    def set_alumnos_view(self, grado_id=None, titulo=None):
        """Manejar el click en los botones de grados y mostrar alumnos por grado especificado"""

        self.reset_view()

        if grado_id is not None or titulo is not None:
            self.grado_selected_id = grado_id
            self.nombre_alumno_selected = titulo

        # Frame Container
        self.main_frame = ttk.Frame(self.wind, borderwidth=0, relief="flat", padding=20)
        self.main_frame.pack(expand=True)

        # Titulo
        main_titulo = ttk.Label(
            self.main_frame,
            text=self.nombre_alumno_selected,
            font=("Sans-serif", 24),
            padding=(0, 30),
        )
        main_titulo.pack(expand=True)

        # Botón "Regresar" posicionado en la esquina superior izquierda
        self.set_change_view_link_corner("Regresar", self.set_reporte_view)

        # Alumnos filtrados por grado de la base de datos
        alumnos = self.run_query(
            """
            SELECT a.alumno_id, a.nombres, a.apellidos, s.seccion FROM grados_secciones gs
            INNER JOIN alumnos a ON gs.grado_seccion_id = a.grado_seccion_id
            INNER JOIN secciones s ON gs.seccion_id = s.seccion_id
            WHERE grado_id = ?
            ORDER BY gs.seccion_id
            """,
            [self.grado_selected_id],
        ).fetchall()

        if len(alumnos) == 0:
            ttk.Label(
                self.main_frame,
                text="No existen alumnos en este grado",
                font=("Sans-serif", 15),
                bootstyle="danger",
            ).pack(expand=True)
            return

        # Agrupamos a los alumnos por sección
        alumnos_grouped = {}
        for alumno in alumnos:
            seccion = alumno[3]
            if seccion not in alumnos_grouped:
                # Si la clave no existe, creamos una nueva lista
                alumnos_grouped[seccion] = []
            # Añadimos la tupla a la lista correspondiente
            alumnos_grouped[seccion].append(alumno)

        # Crear un estilo personalizado y configurarlo para el botón
        estilo = ttk.Style()
        estilo.configure(
            "BotonAlumno.TButton",
            font=("sans-serif", 11),
            width=30,
            justify="center",
        )

        # Configurar variables para el "flex-wrap"
        max_botones_por_fila = 3
        contador_botones_en_fila = 0

        # Contenedor para los alumnos
        alumnos_frame = ttk.Frame(self.main_frame)
        alumnos_frame.pack(expand=True)

        # Agregar cada botón a la UI
        i = 1
        for seccion, alumnos in alumnos_grouped.items():
            # Título de la sección centrado
            ttk.Label(
                alumnos_frame, text=f"Sección: {seccion}", font=("Sans-serif", 14)
            ).pack(fill="x", pady=(10, 5))

            # Configurar una nueva fila para cada sección alineado
            fila_actual = ttk.Frame(alumnos_frame)
            fila_actual.pack(side="top", pady=(0, 5))

            for alumno in alumnos:
                alumno_frame = ttk.Button(
                    fila_actual,
                    text=f"{i}. {(alumno[1]).capitalize()} {alumno[2].capitalize()}",
                    style="BotonAlumno.TButton",
                    command=lambda alumno=alumno[
                        0
                    ], nombre=f"{alumno[1]} {alumno[2]}": self.set_alumno_reporte_view(
                        alumno, nombre
                    ),
                )
                alumno_frame.pack(side="left", padx=5)

                contador_botones_en_fila += 1

                # Verificar si se debe envolver a la siguiente fila
                if contador_botones_en_fila >= max_botones_por_fila:
                    fila_actual = ttk.Frame(alumnos_frame)
                    fila_actual.pack(
                        side="top", pady=(0, 5)
                    )  # Alinear hacia arriba y agregar un espacio en la parte inferior
                    contador_botones_en_fila = 0

                i += 1

    def set_alumno_reporte_view(self, alumno_id, nombre):
        """Mostrar vista con el reporte de asistencia del alumno especificado"""
        self.alumno_selected_id = alumno_id
        self.reset_view()

        # Frame Container
        self.main_frame = ttk.Frame(self.wind, borderwidth=0, relief="flat", padding=20)
        self.main_frame.pack(expand=True)

        # Titulo
        main_titulo = ttk.Label(
            self.main_frame,
            text="Reporte de asistencia",
            font=("Sans-serif", 24),
        )
        main_titulo.pack(expand=True)

        # Subtitulo
        ttk.Label(
            self.main_frame,
            text=f"Alumno: {nombre}",
            font=("Sans-serif", 14),
        ).pack(expand=True)

        # Botón "Regresar" posicionado en la esquina superior izquierda
        self.set_change_view_link_corner("Regresar", self.set_alumnos_view)

        # Asistencias del alumno seleccionado
        asistencias = self.run_query(
            "SELECT llegada FROM asistencias WHERE alumno_id = ?",
            [self.alumno_selected_id],
        ).fetchall()

        if len(asistencias) == 0:
            ttk.Label(
                self.main_frame,
                text="No existen asistencias registradas para este alumno",
                font=("Sans-serif", 15),
                bootstyle="danger",
                padding=(0, 30),
            ).pack(expand=True)
            return

        coldata = [
            {"text": "Año", "stretch": True},
            {"text": "Mes", "stretch": True},
            {"text": "Día", "stretch": True},
            {"text": "Hora", "stretch": True},
        ]

        months_in_spanish = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }
        rowdata = []

        for asistencia in asistencias:
            time = datetime.fromisoformat(asistencia[0])
            row = (
                time.year,
                months_in_spanish[time.month],
                time.day,
                time.strftime("%I:%M:%S %p"),
            )
            rowdata.append(row)

        # Crear tabla
        dt = Tableview(
            master=self.main_frame,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            autofit=True,
            autoalign=True,
        )
        dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Centrar cabeceras y filas de la tabla
        for col_id in dt.view["columns"]:
            dt.view.column(col_id, anchor="center")
            dt.view.heading(col_id, anchor="center")

        # Crear el botón de exportar
        export_button = ttk.Button(
            self.main_frame,
            text="Exportar a Excel",
            command=lambda: self.export_to_excel(dt, nombre),
            bootstyle=SUCCESS,
        )
        export_button.pack(pady=10)

    def export_to_excel(self, table, default_name):
        """Exportar datos de una tabla TableView en formato Excel"""
        # Traer datos de las cabeceras y registros de la tabla
        headers = [col.headertext for col in table.tablecolumns]
        records = [row.values for row in table.tablerows]

        if len(headers) == 0 or len(records) == 0:
            self.display_error_box("No hay datos para exportar en esta tabla")
            return

        # Obtener la ubicación y el nombre del archivo del usuario
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            initialfile=f"{default_name}.xlsx",
        )
        if not file_path:
            self.display_error_box("Ruta inválida para guardar un archivo")
            return

        wb = Workbook()
        ws = wb.active

        # Escribir los encabezados de las columnas
        for col, column_name in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=column_name)

        # Escribir los datos de las filas
        for row, row_data in enumerate(records, start=2):
            for col, data in enumerate(row_data, start=1):
                ws.cell(row=row, column=col, value=data)

        # Guardar el archivo Excel en la ubicación especificada
        wb.save(file_path)

        # Abrir el archivo después de guardarlo
        answer = Messagebox.show_question(
            message="Archivo guardado con éxito. ¿Desea abrirlo?",
            title="Operación exitosa",
            alert=True,
            parent=self.main_frame,
            buttons=["No:secondary", "Sí:primary"],
        )

        if answer.lower() == "sí":
            subprocess.Popen([file_path], shell=True)
        else:
            Messagebox.show_info(
                message=f"Archivo guardado en la ruta {file_path}",
                title="Archivo guardado",
                alert=True,
                parent=self.main_frame,
            )


if __name__ == "__main__":
    # Ventana principal
    window = Tk()

    # Activar modo oscuro
    # style = ttk.Style("darkly")

    app = Main(window, "escuela.db")
    window.mainloop()
