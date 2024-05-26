"""Main controller"""

import sqlite3
from datetime import datetime
from tkinter import Label, LabelFrame, Frame, Entry, Tk
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.constants import END, PRIMARY, INFO
from ttkbootstrap.dialogs.dialogs import Messagebox
import ttkbootstrap as ttk


class Main:
    """Main program"""

    def __init__(self, window_app, db_app):
        self.wind = window_app
        self.db_name = db_app
        self.grado_selected_id = 0
        self.alumno_selected_id = 0

        # Ventana minizada: Ancho y alto de la pantalla a la mitad
        width = self.wind.winfo_screenwidth() / 2
        height = self.wind.winfo_screenheight() / 2
        self.wind.geometry(f"{int(width)}x{int(height)}")

        # Ventanta maximizada: Full
        # self.wind.state("zoomed")

        self.wind.title("Sistema de asistencias")
        self.set_principal_view()

    def reset_view(self):
        """Eliminar todos los widgets de la vista actual"""
        # Eliminar widgets de la vista principal
        for widget in self.wind.winfo_children():
            widget.destroy()

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

    def display_error_box(self, message):
        """Notificación para cuando suceda un error"""
        Messagebox.show_error(title="Advertencia", message=message)

    def register_asistencia(self, _event):
        """Función para registrar asistencia cuando se presione 'Enter' en la vista principal"""
        codigo_alumno = self.input_codigo.get()

        if codigo_alumno in (None, ""):
            return self.display_error_box("Código inválido")

        result = self.run_query(
            "SELECT * FROM alumnos WHERE codigo = ?", [codigo_alumno]
        )
        alumno = result.fetchone()

        if alumno in (None, "") or len(alumno) == 0:
            return self.display_error_box("No se encontró el alumno")

        fecha_actual = datetime.now().isoformat()
        asistencia = self.run_query(
            "INSERT INTO asistencias(alumno_id, fecha) VALUES (?, ?)",
            [alumno[0], fecha_actual],
        )

        if asistencia:
            return self.display_success_toast(
                f"Asistencia marcada para el alumno: {alumno[1]}"
            )

        return self.display_error_box("Error interno al registrar asistencia")

    def set_principal_view(self):
        """Mostrar vista principal"""
        # Frame Container
        main_frame = LabelFrame(self.wind, borderwidth=0, relief="flat")
        main_frame.pack(expand=True)

        # Hero principal
        main_titulo = Label(
            main_frame, text="Esperando código de barras...", font=("Sans-serif", 22)
        )
        main_titulo.pack(expand=True)

        # Frame para el input y el botón
        frame_input_boton = Frame(main_frame)
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
            frame_input_boton, text="Agregar manualmente", bootstyle=PRIMARY
        )
        boton_agregar.pack(side="left", padx=10, pady=20)
        boton_agregar.bind("<Button-1>", self.register_asistencia)

        # Escuchador de evento "Enter" a la ventana principal
        self.wind.bind("<Return>", self.register_asistencia)

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
        main_frame = ttk.LabelFrame(self.wind, borderwidth=0, relief="flat", padding=5)
        main_frame.pack(side="top")

        # Titulo
        main_titulo = Label(
            main_frame, text="GRADOS DISPONIBLES", font=("Sans-serif", 24)
        )
        main_titulo.pack(expand=True)

        # Grados registrados en la base de datos
        result = self.run_query(
            """
            SELECT g.grado_id, g.grado, n.nivel FROM grados g
            INNER JOIN niveles n ON g.nivel_id = n.nivel_id
            """
        )
        grados = result.fetchall()

        # Contenedor para los grados
        grados_frame = ttk.Frame(main_frame)
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
            grado_frame = ttk.Button(
                fila_actual,
                text=f"{grado[0]}. {(grado[1]).capitalize()} de {grado[2]}",
                style="BotonGrado.TButton",
                command=lambda grado=grado[
                    0
                ], nombre=f"{grado[1].capitalize()} de {grado[2]}": self.set_alumnos_view(
                    grado, nombre
                ),
            )
            grado_frame.pack(side="left", padx=5, pady=5)

            contador_botones_en_fila += 1

            # Verificar si se debe envolver a la siguiente fila
            if contador_botones_en_fila >= max_botones_por_fila:
                fila_actual = ttk.Frame(grados_frame)
                fila_actual.pack(side="top", pady=5)
                contador_botones_en_fila = 0

    # CAMBIAR EL ESCUCHADOR DE EVENTOS PARA EVITAR PASARLE EL GRADO_ID Y NOMBRE A LA
    # FUNCIÓN SINO QUE ESTÉ GUARDADO GLOBALMENTE EN UN ATRIBUTO DE LA CLASE
    def set_alumnos_view(self, grado_id, nombre):
        """Manejar el click en los botones de grados y mostrar alumnos por grado especificado"""
        self.grado_selected_id = grado_id
        self.reset_view()

        # Frame Container
        main_frame = ttk.LabelFrame(self.wind, borderwidth=0, relief="flat", padding=5)
        main_frame.pack(side="top")

        # Titulo
        Label(
            main_frame, text=f"Alumnos del grado: {nombre}", font=("Sans-serif", 24)
        ).pack(expand=True)

        # Alumnos filtrados por grado de la base de datos
        result = self.run_query(
            "SELECT * FROM alumnos WHERE grado_id = ?", [self.grado_selected_id]
        )
        alumnos = result.fetchall()

        # Contenedor para los alumnos
        alumnos_frame = ttk.Frame(main_frame)
        alumnos_frame.pack(expand=True)

        if len(alumnos) == 0:
            ttk.Label(
                alumnos_frame,
                text="No existen alumnos en este grado",
                font=("Sans-serif", 15),
                bootstyle="danger",
            ).pack(expand=True)
        else:
            # Configurar variables para el "flex-wrap"
            max_botones_por_fila = 3
            fila_actual = ttk.Frame(alumnos_frame)
            fila_actual.pack(side="top", pady=5)
            contador_botones_en_fila = 0

            # Crear un estilo personalizado
            estilo = ttk.Style()

            # Configurar el tamaño de la fuente para el estilo del botón
            estilo.configure(
                "BotonAlumno.TButton",
                font=("sans-serif", 11),
                width=30,
                justify="center",
            )

            # Agregar cada botón a la UI
            i = 1
            for alumno in alumnos:
                alumno_frame = ttk.Button(
                    fila_actual,
                    text=f"{i}. {(alumno[1]).capitalize()} {alumno[2]}",
                    style="BotonAlumno.TButton",
                    command=lambda alumno=alumno[
                        0
                    ], nombre=f"{alumno[1]} {alumno[2]}": self.set_alumno_reporte_view(
                        alumno, nombre
                    ),
                )
                alumno_frame.pack(side="left", padx=5, pady=5)

                contador_botones_en_fila += 1

                # Verificar si se debe envolver a la siguiente fila
                if contador_botones_en_fila >= max_botones_por_fila:
                    fila_actual = ttk.Frame(alumnos_frame)
                    fila_actual.pack(side="top", pady=5)
                    contador_botones_en_fila = 0

                i += 1

        # Botón "Regresar" posicionado en la esquina superior izquierda
        boton_regresar = ttk.Button(
            self.wind,
            text="Regresar",
            bootstyle=INFO,
            command=self.set_reporte_view,
        )
        boton_regresar.place(relx=1.0, y=25, x=-30, anchor="ne")

    def set_alumno_reporte_view(self, alumno_id, nombre):
        """Mostrar vista con el reporte de asistencia del alumno especificado"""
        self.alumno_selected_id = alumno_id
        self.reset_view()

        # Frame Container
        main_frame = ttk.LabelFrame(self.wind, borderwidth=0, relief="flat", padding=5)
        main_frame.pack(side="top")

        # Titulo
        Label(main_frame, text="Reporte de Asistencia", font=("Sans-serif", 24)).pack(
            expand=True
        )

        # Texto inferior
        Label(main_frame, text=f"Alumno: {nombre}", font=("Sans-serif", 15)).pack(
            side="left"
        )

        # Alumnos filtrados por grado de la base de datos
        # result = self.run_query(
        #     "SELECT * FROM alumnos WHERE grado_id = ?", [self.grado_selected_id]
        # )
        # alumnos = result.fetchall()

        # # Contenedor para los alumnos
        # alumnos_frame = ttk.Frame(main_frame)
        # alumnos_frame.pack(expand=True)

        # if len(alumnos) == 0:
        #     ttk.Label(
        #         alumnos_frame,
        #         text="No existen alumnos en este grado",
        #         font=("Sans-serif", 15),
        #         bootstyle="danger",
        #     ).pack(expand=True)
        # else:
        #     # Configurar variables para el "flex-wrap"
        #     max_botones_por_fila = 3
        #     fila_actual = ttk.Frame(alumnos_frame)
        #     fila_actual.pack(side="top", pady=5)
        #     contador_botones_en_fila = 0

        #     # Crear un estilo personalizado
        #     estilo = ttk.Style()

        #     # Configurar el tamaño de la fuente para el estilo del botón
        #     estilo.configure(
        #         "BotonAlumno.TButton",
        #         font=("sans-serif", 11),
        #         width=30,
        #         justify="center",
        #     )

        #     # Agregar cada botón a la UI
        #     i = 1
        #     for alumno in alumnos:
        #         alumno_frame = ttk.Button(
        #             fila_actual,
        #             text=f"{i}. {(alumno[1]).capitalize()} {alumno[2]}",
        #             style="BotonAlumno.TButton",
        #             # command=lambda alumno=alumno[0]: self.set_alumno_reporte_view(
        #             #     alumno
        #             # ),
        #         )
        #         alumno_frame.pack(side="left", padx=5, pady=5)

        #         contador_botones_en_fila += 1

        #         # Verificar si se debe envolver a la siguiente fila
        #         if contador_botones_en_fila >= max_botones_por_fila:
        #             fila_actual = ttk.Frame(alumnos_frame)
        #             fila_actual.pack(side="top", pady=5)
        #             contador_botones_en_fila = 0

        #         i += 1

        # Botón "Regresar" posicionado en la esquina superior izquierda
        boton_regresar = ttk.Button(
            self.wind,
            text="Regresar",
            bootstyle=INFO,
            command=self.set_alumnos_view,
        )
        boton_regresar.place(relx=1.0, y=25, x=-30, anchor="ne")


if __name__ == "__main__":
    # Ventana principal
    window = Tk()

    # Activar modo oscuro
    # style = ttk.Style("darkly")

    app = Main(window, "escuela.db")
    window.mainloop()
