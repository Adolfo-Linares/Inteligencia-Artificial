import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox

URL_API = "http://127.0.0.1:5002/completar"

def generar_codigo():

    texto = entrada.get("1.0", tk.END).strip()

    if texto == "":
        messagebox.showwarning("Aviso", "Escribe algo primero")
        return

    try:
        respuesta = requests.post(
            URL_API,
            json={
                "prompt": texto
            }
        )

        datos = respuesta.json()

        salida.delete("1.0", tk.END)
        salida.insert(tk.END, datos["resultado"])

    except Exception as e:
        messagebox.showerror(
            "Error",
            "No se pudo conectar con el servidor.\n\nRevisa que servidor.py este corriendo."
        )

def limpiar():

    entrada.delete("1.0", tk.END)
    salida.delete("1.0", tk.END)

ventana = tk.Tk()
ventana.title("Asistente de Codigo con RNN")
ventana.geometry("900x650")
ventana.configure(bg="#1e1e2f")

titulo = tk.Label(
    ventana,
    text="Asistente de Codigo Personalizado",
    font=("Arial", 22, "bold"),
    bg="#1e1e2f",
    fg="white"
)
titulo.pack(pady=15)

subtitulo = tk.Label(
    ventana,
    text="Escribe el inicio de una funcion en C y la RNN intentara completarla",
    font=("Arial", 12),
    bg="#1e1e2f",
    fg="#cfcfcf"
)
subtitulo.pack(pady=5)

marco = tk.Frame(ventana, bg="#1e1e2f")
marco.pack(pady=10)

label_entrada = tk.Label(
    marco,
    text="Texto de entrada:",
    font=("Arial", 13, "bold"),
    bg="#1e1e2f",
    fg="white"
)
label_entrada.grid(row=0, column=0, sticky="w", padx=10)

entrada = scrolledtext.ScrolledText(
    marco,
    width=95,
    height=7,
    font=("Consolas", 12),
    bg="#2b2b3d",
    fg="white",
    insertbackground="white"
)
entrada.grid(row=1, column=0, padx=10, pady=8)

botones = tk.Frame(ventana, bg="#1e1e2f")
botones.pack(pady=10)

boton_generar = tk.Button(
    botones,
    text="Generar sugerencia",
    command=generar_codigo,
    font=("Arial", 12, "bold"),
    bg="#00c853",
    fg="white",
    padx=20,
    pady=10,
    cursor="hand2"
)
boton_generar.grid(row=0, column=0, padx=10)

boton_limpiar = tk.Button(
    botones,
    text="Limpiar",
    command=limpiar,
    font=("Arial", 12, "bold"),
    bg="#ff5252",
    fg="white",
    padx=20,
    pady=10,
    cursor="hand2"
)
boton_limpiar.grid(row=0, column=1, padx=10)

label_salida = tk.Label(
    ventana,
    text="Sugerencia generada:",
    font=("Arial", 13, "bold"),
    bg="#1e1e2f",
    fg="white"
)
label_salida.pack(anchor="w", padx=35)

salida = scrolledtext.ScrolledText(
    ventana,
    width=95,
    height=16,
    font=("Consolas", 12),
    bg="#111827",
    fg="#00ff99",
    insertbackground="white"
)
salida.pack(padx=30, pady=10)

ejemplos = tk.Label(
    ventana,
    text="Ejemplos: int sumar    |    float dividir    |    int esPar    |    int factorial",
    font=("Arial", 11),
    bg="#1e1e2f",
    fg="#a5b4fc"
)
ejemplos.pack(pady=8)

ventana.mainloop()