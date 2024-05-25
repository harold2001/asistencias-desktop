"""Main controller"""

from tkinter import *
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as ttk


class Main:
    """Main program"""

    def __init__(self, window_app):
        self.wind = window_app

        # Ventana minizada: Ancho y alto de la pantalla a la mitad
        width = self.wind.winfo_screenwidth() / 2
        height = self.wind.winfo_screenheight() / 2
        self.wind.geometry(f"{int(width)}x{int(height)}")

        # Ventanta maximizada: Full
        # self.wind.state("zoomed")

        self.wind.title("Sistema de asistencias")
        self.set_principal_view()

    def set_principal_view(self):
        """Mostrar vista principal"""
        # Frame Container
        main_frame = LabelFrame(self.wind, borderwidth=0, relief="flat")
        main_frame.pack(expand=True)

        # Hero principal
        main_titulo = Label(
            main_frame, text="Esperando código de barras...", font=("Sans-serif", 20)
        )
        main_titulo.pack(expand=True)

        # Frame para el input y el botón
        frame_input_boton = Frame(main_frame)
        frame_input_boton.pack(expand=True)

        # Input código de barras
        self.input_codigo = Entry(frame_input_boton, font=("Helvetica", 14))
        self.input_codigo.pack(side="left")
        self.input_codigo.focus()

        # Evento Ctrl + Delete
        self.input_codigo.bind("<Control-BackSpace>", self.reset_input_codigo)

        # Botón "agregar manualmente"
        boton_agregar = ttk.Button(
            frame_input_boton, text="Agregar manualmente", bootstyle=SUCCESS
        )
        boton_agregar.pack(side="left", padx=10, pady=20)
        boton_agregar.bind("<Button-1>", self.on_enter_main)

        # Escuchador de evento "Enter" a la ventana principal
        self.wind.bind("<Return>", self.on_enter_main)

    def on_enter_main(self, event):
        """Función para cuando se presione 'Enter' en la vista principal"""
        print(event)

    def reset_input_codigo(self, event):
        """Ctrl + Delete -> Borrar todo el contenido del input"""
        print(event)
        self.input_codigo.delete(0, tk.END)


if __name__ == "__main__":
    window = tk.Tk()
    app = Main(window)
    window.mainloop()
