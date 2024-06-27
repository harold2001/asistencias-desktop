"""Main controller"""

import sqlite3
import subprocess
from datetime import datetime
from tkinter import Frame, Entry, Tk, filedialog, Menu
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.constants import END, PRIMARY, INFO, YES, BOTH, SUCCESS
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.scrolled import ScrolledFrame
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
        # self.wind.state("zoomed")

        self.wind.title("Sistema de asistencias")
        self.menubar = Menu(self.wind)

        # Crear menús si aún no existen
        if not self.menubar.index("end"):
            # Asistencias
            asistencias_menu = Menu(self.menubar, tearoff=0)
            asistencias_menu.add_command(
                label="Marcar asistencia", command=self.set_principal_view
            )
            self.menubar.add_cascade(label="Asistencias", menu=asistencias_menu)

            # Reportes
            reportes_menu = Menu(self.menubar, tearoff=0)
            reportes_menu.add_command(
                label="General", command=self.set_reporte_general_view
            )
            reportes_menu.add_command(
                label="Por alumno", command=self.set_reporte_alumno_view
            )
            reportes_menu.add_command(
                label="Por grado y sección", command=self.set_reporte_grado_view
            )
            self.menubar.add_cascade(label="Reportes", menu=reportes_menu)

            self.wind.config(menu=self.menubar)

            # Alumnos
            reportes_menu = Menu(self.menubar, tearoff=0)
            reportes_menu.add_command(
                label="Agregar", command=self.set_reporte_general_view
            )
            reportes_menu.add_command(
                label="Ver todos", command=self.set_reporte_alumno_view
            )
            self.menubar.add_cascade(label="Alumnos", menu=reportes_menu)

            self.wind.config(menu=self.menubar)

        self.set_principal_view()

    def reset_view(self, main_title):
        """Eliminar todos los widgets de la vista actual"""
        # Eliminar widgets de la vista principal
        for widget in self.wind.winfo_children():
            if widget.winfo_class() != "Menu":
                widget.destroy()

        # Quitar el escuchador de eventos "Enter" de la ventana principal
        self.wind.unbind("<Return>")

        # Frame Container
        self.main_frame = ttk.Frame(self.wind, borderwidth=0, relief="flat", padding=20)
        self.main_frame.pack(expand=True)

        # Titulo
        main_titulo = ttk.Label(
            self.main_frame,
            text=main_title,
            font=("Sans-serif", 26),
        )
        main_titulo.pack(expand=True)

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
        boton_reporte.place(relx=0.0, y=25, x=30, anchor="nw")

    def register_asistencia(self, codigo_alumno):
        """Función para registrar asistencia cuando se presione 'Enter' en la vista principal"""
        if codigo_alumno in (None, ""):
            return self.display_error_box("Código inválido")

        result = self.run_query(
            "SELECT alumno_id, nombres, apellido_paterno FROM alumnos WHERE codigo = ?",
            [codigo_alumno],
        )
        alumno = result.fetchone()

        if alumno in (None, "") or len(alumno) == 0:
            return self.display_error_box("No se encontró el alumno")

        now = datetime.now()
        hora_entrada = now.strftime("%H:%M:%S")
        fecha = now.strftime("%Y-%m-%d")

        asistencia = self.run_query(
            "INSERT INTO asistencias(alumno_id, hora_entrada, fecha) VALUES (?, ?, ?)",
            [alumno[0], hora_entrada, fecha],
        )

        if asistencia:
            return self.display_success_toast(
                f"Asistencia marcada para el alumno: {alumno[1]} {alumno[2]}"
            )

        return self.display_error_box("Error interno al registrar asistencia")

    def export_to_excel(
        self, table, default_name, alumno_grado=None, alumno_seccion=None
    ):
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

        # Celda A1
        ws.cell(row=1, column=1, value="ALUMNO:")
        # Combinar las celdas B1, C1 y D1
        ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=4)
        ws.cell(row=1, column=2, value=default_name)

        # Celda B1 y B2
        ws.cell(row=2, column=1, value="GRADO:")
        ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=4)
        ws.cell(row=2, column=2, value=alumno_grado)

        # Celda C1 y C2
        ws.cell(row=3, column=1, value="SECCIÓN:")
        ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=4)
        ws.cell(row=3, column=2, value=alumno_seccion)

        # Escribir los encabezados de las columnas
        for col, column_name in enumerate(headers, start=1):
            ws.cell(row=4, column=col, value=column_name)

        # Escribir los datos de las filas
        for row, row_data in enumerate(records, start=5):
            for col, data in enumerate(row_data, start=1):
                ws.cell(row=row, column=col, value=data)

        # Guardar el archivo Excel en la ubicación especificada
        try:
            wb.save(file_path)
        except PermissionError:
            self.display_error_box(
                "No se pudo guardar el archivo. Permiso denegado. Cierre el archivo."
            )
            return

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

    def set_principal_view(self):
        """Mostrar vista principal"""
        self.reset_view("Esperando código de barras...")
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

    def set_reporte_general_view(self):
        """Mostrar segunda vista con todos los grados disponibles"""
        self.reset_view("Reporte general mensual")

        # Debajo del título
        ttk.Label(
            self.main_frame,
            text="Selecciona un grado y sección:",
            font=("Sans-Serif", 11),
        ).pack(fill="x", pady=(30, 20))

        # Grados
        grados = self.run_query(
            "SELECT grado_id, grado FROM grados WHERE grado_id >= 7"
        ).fetchall()
        grados_dict = {grado: grado_id for grado_id, grado in grados}
        combobox_grados = ttk.Combobox(
            self.main_frame,
            bootstyle="primary",
            values=list(grados_dict.keys()),
            state="readonly",
        )
        combobox_grados.set("Grado")
        combobox_grados.pack(pady=20, padx=20, side="left")

        # Secciones
        secciones = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        combobox_secciones = ttk.Combobox(
            self.main_frame, bootstyle="primary", values=secciones, state="readonly"
        )
        combobox_secciones.set("Sección")
        combobox_secciones.pack(pady=20, padx=20, side="left")

        def set_validate_report():
            """Validar los datos y mostrar el reporte"""
            grado = combobox_grados.get()
            seccion = combobox_secciones.get()
            if grado == "Grado" or seccion == "Sección":
                self.display_error_box("Selecciona un grado y sección")
                return

            self.set_reporte_general_table(
                grados_dict[grado],
                grado,
                seccion,
            )

        ttk.Button(
            self.main_frame,
            text="Buscar",
            bootstyle=PRIMARY,
            padding=(20, 10),
            command=set_validate_report,
        ).pack(expand=True, fill="x")

    def set_reporte_general_table(self, grado_id, grado, seccion):
        """Mostrar tabla con datos de la búsqueda por grado y seccion de manera mensual"""
        self.reset_view(grado)
        self.set_change_view_link_corner(
            "Volver al buscador", self.set_reporte_general_view
        )

        print(grado_id)
        # Datos del grado
        datos_frame = ttk.Frame(self.main_frame, width=100)
        datos_frame.pack(expand=True, fill="x", padx=0, pady=(30, 20))

        ttk.Label(
            datos_frame,
            text=f"Sección: {seccion}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="nw",
        ).pack(expand=True, fill="x")

        # MOSTRAR REPORTE MENSUAL!

    def set_reporte_alumno_view(self):
        """Buscar un alumno por nombre y mostrar su reporte de asistencias en otra vista"""
        self.reset_view("Buscar por alumno")

        # Debajo del título
        ttk.Label(
            self.main_frame,
            text="Escribe el nombre de un alumno y luego dale click para ver su reporte:",
            font=("Sans-Serif", 11),
        ).pack(fill="x", pady=(30, 20))

        # Frame para el Entry y el botón
        frame_input_boton = Frame(self.main_frame)
        frame_input_boton.pack(expand=True)

        # Frame para el input y resultados
        frame_entry_list = Frame(frame_input_boton)
        frame_entry_list.pack(side="left", fill="x", padx=(0, 10))

        # Input nombre del alumno
        nombre_alumno = Entry(
            frame_entry_list,
            font=("Helvetica", 18),
            justify="center",
        )
        nombre_alumno.config(width=60)
        nombre_alumno.focus()
        nombre_alumno.pack(expand=True)

        # Lista de opciones para mostrar los resultados
        frame_resultados = ScrolledFrame(frame_entry_list, padding=0, height=300)
        frame_resultados.pack(fill="x", expand=YES)
        frame_resultados.hide_scrollbars()
        frame_resultados.disable_scrolling()

        # Evento KeyPress
        nombre_alumno.bind(
            "<KeyRelease>",
            lambda event: self.set_reporte_alumno_opciones(
                nombre_alumno.get(), frame_resultados
            ),
        )

        # Evento Ctrl + Delete
        nombre_alumno.bind(
            "<Control-BackSpace>", lambda event: nombre_alumno.delete(0, END)
        )

    def set_reporte_alumno_opciones(self, nombre, resultados_frame):
        """Mostrar opciones debajo del buscador"""
        # Limpiar resultados anteriores
        for widget in resultados_frame.winfo_children():
            widget.destroy()

        if nombre:
            match = self.run_query(
                """
                SELECT
                    a.alumno_id,
                    a.codigo,
                    a.nombres,
                    a.apellido_paterno,
                    a.apellido_materno,
                    g.grado,
                    dg.seccion
                FROM
                    alumnos a
                INNER JOIN detalle_grados dg 
                    ON
                    dg.detalle_grado_id = a.detalle_grado_id
                INNER JOIN grados g 
                    ON
                    g.grado_id = dg.grado_id
                WHERE
                    nombres LIKE ?
                    OR apellido_paterno LIKE ?
                    OR apellido_materno LIKE ?
            """,
                [f"%{nombre}%", f"%{nombre}%", f"%{nombre}%"],
            ).fetchall()

            stylebtn = ttk.Style()
            stylebtn.configure("Custom.TButton", font=("Sans-Serif", 11))

            for alumno in match:
                ttk.Button(
                    resultados_frame,
                    text=f'{alumno[2]} {alumno[3]} {alumno[4]} - {alumno[5]} "{alumno[6]}"',
                    bootstyle=INFO,
                    command=lambda alumno=alumno: self.set_reporte_alumno_table(alumno),
                    style="Custom.TButton",
                    padding=10,
                ).pack(fill="x", expand=True)
            resultados_frame.show_scrollbars()
            resultados_frame.enable_scrolling()
        else:
            resultados_frame.config(height=0)
            resultados_frame.hide_scrollbars()
            resultados_frame.disable_scrolling()

    def set_reporte_alumno_table(self, alumno):
        """Mostrar vista con el reporte de asistencia del alumno especificado"""
        self.reset_view("Reporte por alumno")
        self.set_change_view_link_corner(
            "Volver al buscador", self.set_reporte_alumno_view
        )
        alumno_nombre = f"{alumno[2]} {alumno[3]} {alumno[4]}"

        # Datos del alumno
        datos_frame = ttk.Frame(self.main_frame, width=80)
        datos_frame.pack(expand=True, fill="x", padx=0, pady=(30, 20))

        ttk.Label(
            datos_frame,
            text=f"Alumno: {alumno_nombre}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="w",
        ).pack(expand=True, fill="x")

        ttk.Label(
            datos_frame,
            text=f"Grado: {alumno[5]}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="w",
        ).pack(expand=True, fill="x")

        ttk.Label(
            datos_frame,
            text=f"Sección: {alumno[6]}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="w",
        ).pack(expand=True, fill="x")

        # Asistencias del alumno seleccionado
        asistencias = self.run_query(
            "SELECT hora_entrada, hora_salida, fecha FROM asistencias WHERE alumno_id = ?",
            [alumno[0]],
        ).fetchall()

        if len(asistencias) == 0:
            ttk.Label(
                self.main_frame,
                text="No existen asistencias registradas para este alumno",
                font=("Sans-serif", 15),
                bootstyle="danger",
                padding=(0, 30),
                justify="center",
            ).pack(expand=True, fill="x")
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
            time = datetime.strptime(asistencia[2], "%Y-%m-%d")
            entrada = datetime.strptime(asistencia[0], "%H:%M:%S")
            row = (
                time.year,
                months_in_spanish[time.month],
                time.day,
                entrada.strftime("%I:%M:%S %p"),
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
            command=lambda: self.export_to_excel(
                dt, alumno_nombre, alumno[5], alumno[6]
            ),
            bootstyle=SUCCESS,
        )
        export_button.pack(pady=10)

    def set_reporte_grado_view(self):
        """Vista del reporte por grado y seccion"""
        self.reset_view("Reporte por grado y sección")

        # Debajo del título
        ttk.Label(
            self.main_frame,
            text="Selecciona un grado, sección y fecha para ver un reporte específico:",
            font=("Sans-Serif", 11),
        ).pack(fill="x", pady=(30, 20))

        # Grados
        grados = self.run_query(
            "SELECT grado_id, grado FROM grados WHERE grado_id >= 7"
        ).fetchall()
        grados_dict = {grado: grado_id for grado_id, grado in grados}
        combobox_grados = ttk.Combobox(
            self.main_frame,
            bootstyle="primary",
            values=list(grados_dict.keys()),
            state="readonly",
        )
        combobox_grados.set("Grado")
        combobox_grados.pack(pady=20, padx=20, side="left")

        # Secciones
        secciones = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        combobox_secciones = ttk.Combobox(
            self.main_frame, bootstyle="primary", values=secciones, state="readonly"
        )
        combobox_secciones.set("Sección")
        combobox_secciones.pack(pady=20, padx=20, side="left")

        # Fecha
        date_entry = ttk.DateEntry(
            self.main_frame, bootstyle="primary", dateformat="%d-%m-%Y"
        )
        date_entry.pack(expand=True, side="left", padx=20, pady=20)

        def set_validate_report():
            """Validar los datos y mostrar el reporte"""
            grado = combobox_grados.get()
            seccion = combobox_secciones.get()
            fecha = date_entry.entry.get()
            if grado == "Grado" or seccion == "Sección":
                self.display_error_box("Selecciona un grado y sección")
                return

            self.set_reporte_grado_table(
                grados_dict[grado],
                grado,
                seccion,
                fecha,
            )

        ttk.Button(
            self.main_frame,
            text="Buscar",
            bootstyle=PRIMARY,
            padding=(20, 10),
            command=set_validate_report,
        ).pack(expand=True, fill="x")

    def set_reporte_grado_table(self, grado_id, grado, seccion, fecha):
        """Mostrar tabla con datos de la búsqueda por grado, seccion y fecha"""
        self.reset_view(grado)
        self.set_change_view_link_corner(
            "Volver al buscador", self.set_reporte_grado_view
        )

        fecha_datetime = datetime.strptime(fecha, "%d-%m-%Y")

        # Datos del grado
        datos_frame = ttk.Frame(self.main_frame, width=100)
        datos_frame.pack(expand=True, fill="x", padx=0, pady=(30, 20))

        ttk.Label(
            datos_frame,
            text=f"Sección: {seccion}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="nw",
        ).pack(expand=True, fill="x")

        ttk.Label(
            datos_frame,
            text=f"Fecha: {fecha}",
            font=("Sans-serif", 11),
            justify="left",
            anchor="nw",
        ).pack(expand=True, fill="x")

        # Asistencias del grado y seccion seleccionado
        asistencias = self.run_query(
            """
            SELECT
                an.hora_entrada,
                an.hora_salida,
                al.codigo,
                al.nombres,
                al.apellido_paterno,
                al.apellido_materno
            FROM
                asistencias an
            INNER JOIN alumnos al ON
                an.alumno_id = al.alumno_id
            INNER JOIN detalle_grados dg ON
                al.detalle_grado_id = dg.detalle_grado_id
            WHERE
                dg.grado_id = ?
                AND dg.seccion = ?
                AND an.fecha = ?;
            """,
            [grado_id, seccion, fecha_datetime.strftime("%Y-%m-%d")],
        ).fetchall()

        if len(asistencias) == 0:
            ttk.Label(
                self.main_frame,
                text="No existen asistencias registradas para esta fecha, sección y grado juntos.",
                font=("Sans-serif", 15),
                bootstyle="danger",
                padding=(0, 30),
                justify="center",
            ).pack(expand=True, fill="x")
            return

        coldata = [
            {"text": "Código", "stretch": True},
            {"text": "Nombre", "stretch": True},
            {"text": "Hora de entrada", "stretch": True},
            {"text": "Hora de salida", "stretch": True},
            {"text": "Fecha", "stretch": True},
        ]
        rowdata = []

        for asistencia in asistencias:
            entrada = datetime.strptime(asistencia[0], "%H:%M:%S")

            if asistencia[1] is None:
                salida = ""
            else:
                salida = datetime.strptime(asistencia[1], "%H:%M:%S").strftime(
                    "%I:%M %p"
                )

            row = (
                asistencia[2],
                f"{asistencia[3]} {asistencia[4]} {asistencia[5]}",
                entrada.strftime("%I:%M %p"),
                salida,
                fecha,
            )
            rowdata.append(row)

        ttk.Label(
            self.main_frame,
            text="Escribe y presiona ENTER para buscar",
            font=("Sans-serif", 10),
            justify="left",
            anchor="nw",
        ).pack(expand=True, fill="x")

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
        # export_button = ttk.Button(
        #     self.main_frame,
        #     text="Exportar a Excel",
        #     command=lambda: self.export_to_excel(dt, grado),
        #     bootstyle=SUCCESS,
        # )
        # export_button.pack(pady=10)


if __name__ == "__main__":
    # Ventana principal
    window = Tk()

    # Activar modo oscuro
    style = ttk.Style("darkly")

    app = Main(window, "escuela.db")
    window.mainloop()
