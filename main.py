import tkinter as tk
from tkinter import messagebox, ttk, Frame
from db import inicializar_db, guardar_simulacion, obtener_historial
from calculos import calcular_interes_simple, calcular_interes_compuesto, calcular_aportaciones_periodicas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def interfaz_grafica():
    ventana = tk.Tk()
    ventana.title("Simulador Avanzado de Inversión")
    ventana.geometry("800x600")

    # Marco principal dividido en secciones
    frame_datos = Frame(ventana, padx=10, pady=10)
    frame_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_grafico = Frame(ventana, padx=10, pady=10, bg="white")
    frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Variables
    tipo_inversion = tk.StringVar(value="compuesto")
    entrada_monto = tk.Entry(frame_datos)
    entrada_tasa = tk.Entry(frame_datos)
    entrada_plazo = tk.Entry(frame_datos)

    # Crear elementos para ingresar datos
    tk.Label(frame_datos, text="Selecciona el tipo de inversión:").pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Interés Compuesto", variable=tipo_inversion, value="compuesto").pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Interés Simple", variable=tipo_inversion, value="simple").pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Aportaciones Periódicas", variable=tipo_inversion, value="periodicas").pack(anchor="w")

    tk.Label(frame_datos, text="Monto inicial (S/):").pack(anchor="w")
    entrada_monto.pack(fill=tk.X)
    tk.Label(frame_datos, text="Tasa de interés (%):").pack(anchor="w")
    entrada_tasa.pack(fill=tk.X)
    tk.Label(frame_datos, text="Plazo (años):").pack(anchor="w")
    entrada_plazo.pack(fill=tk.X)

    # Función para calcular y actualizar el gráfico
    def calcular_y_graficar():
        try:
            # Recuperar datos
            monto = float(entrada_monto.get())
            tasa = float(entrada_tasa.get())
            plazo = int(entrada_plazo.get())

            # Calcular resultados
            if tipo_inversion.get() == "compuesto":
                resultado = calcular_interes_compuesto(monto, tasa, plazo)
            elif tipo_inversion.get() == "simple":
                resultado = calcular_interes_simple(monto, tasa, plazo)
            else:
                resultado = calcular_aportaciones_periodicas(monto, tasa, plazo)

            # Guardar simulación
            guardar_simulacion(tipo_inversion.get(), monto, tasa, plazo, resultado)
            messagebox.showinfo("Resultado", f"Capital final: S/ {resultado:.2f}")

            # Actualizar gráfico
            mostrar_grafico(tipo_inversion.get(), monto, tasa, plazo)

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores válidos.")

    # Función para mostrar el gráfico
    def mostrar_grafico(tipo, monto, tasa, plazo):
        # Configurar la figura
        figure = plt.Figure(figsize=(6, 5), dpi=100)
        ax = figure.add_subplot(111)

        # Calcular datos para el gráfico
        anios = list(range(1, plazo + 1))
        if tipo == "compuesto":
            valores = [calcular_interes_compuesto(monto, tasa, t) for t in anios]
        elif tipo == "simple":
            valores = [calcular_interes_simple(monto, tasa, t) for t in anios]
        else:
            valores = [calcular_aportaciones_periodicas(monto, tasa, t) for t in anios]

        # Graficar
        ax.plot(anios, valores, marker='o', label=f"{tipo.capitalize()}")
        ax.set_title("Proyección de Inversión")
        ax.set_xlabel("Años")
        ax.set_ylabel("Capital (S/)")
        ax.legend()
        ax.grid()

        # Limpiar el marco del gráfico y renderizar el nuevo gráfico
        for widget in frame_grafico.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(figure, frame_grafico)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    # Botones
    tk.Button(frame_datos, text="Calcular y Graficar", command=calcular_y_graficar).pack(pady=10, fill=tk.X)

    # Inicializar la interfaz
    ventana.mainloop()


if __name__ == "__main__":
    inicializar_db()
    interfaz_grafica()
