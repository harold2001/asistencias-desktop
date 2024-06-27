import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk


def dummy_command():
    print("Comando ejecutado")


def main():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Ejemplo de menú con ttkbootstrap")

    # Aplicar el estilo ttkbootstrap
    style = Style(
        "cosmo"
    )  # Puedes cambiar el tema a otro disponible, como "litera", "minty", etc.
    style.master = root

    # Crear el menú principal
    menubar = tk.Menu(root)

    # Crear el primer menú
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Abrir", command=dummy_command)
    file_menu.add_command(label="Guardar", command=dummy_command)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=root.quit)
    menubar.add_cascade(label="Archivo", menu=file_menu)

    # Crear el segundo menú debajo de la barra superior
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Cortar", command=dummy_command)
    edit_menu.add_command(label="Copiar", command=dummy_command)
    # edit_menu.add_command(label="Pegar", command(destroy_window))
    menubar.add_cascade(label="Editar", menu=edit_menu)

    # Configurar la barra de menú en la ventana principal
    root.config(menu=menubar)

    # Agregar un botón de prueba debajo del menú
    button = ttk.Button(root, text="Click me!", command=dummy_command)
    button.pack(padx=10, pady=10)

    # Iniciar el bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()
