import tkinter as tk
from tkinter import messagebox, ttk, Frame
from db import inicializar_db, guardar_simulacion, obtener_historial
from calculos import calcular_interes_simple, calcular_interes_compuesto, calcular_aportaciones_periodicas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image, ImageTk
from apis import APIsFinancierasPeru


def obtener_tasa_interes_actual():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    data = response.json()
    return data['rates']['PEN']  # Ejemplo de tasa de cambio USD a PEN

def simulacion_monte_carlo(monto, tasa, plazo, num_simulaciones=1000):
    resultados = []
    for _ in range(num_simulaciones):
        tasa_simulada = np.random.normal(tasa, 0.02)  # Ejemplo de desviación estándar del 2%
        resultado = calcular_interes_compuesto(monto, tasa_simulada, plazo)
        resultados.append(resultado)
    return resultados

class DatosFinancierosPeru:
    def __init__(self):
        self.api_key = "TU_API_KEY"  # Reemplazar con tu API key
        
    def obtener_tasa_referencia_bcrp(self):
        """Obtiene la tasa de referencia del BCRP"""
        # Implementar llamada a API del BCRP
        pass
        
    def obtener_inflacion_actual(self):
        """Obtiene la tasa de inflación actual de Perú"""
        # Implementar llamada a API
        pass
        
    def obtener_rendimiento_bonos_soberanos(self):
        """Obtiene el rendimiento de los bonos soberanos peruanos"""
        # Implementar llamada a API
        pass

def interfaz_grafica():
    ventana = tk.Tk()
    ventana.title("Simulador Avanzado de Inversión")
    ventana.geometry("800x600")
    ventana.configure(bg="#f0f0f0")

    # Agregar ícono y logo
    # ventana.iconbitmap("assets/icon.ico")  # Comentar o eliminar esta línea si no tienes el archivo

    try:
        logo = Image.open("assets/logo.png")
        logo = logo.resize((200, 100), Image.LANCZOS)  # Reemplaza ANTIALIAS por LANCZOS
        logo = ImageTk.PhotoImage(logo)
        tk.Label(ventana, image=logo, bg="#f0f0f0").pack(pady=10)
    except FileNotFoundError:
        print("No se pudo cargar el logo. Asegúrate de que el archivo 'logo.png' esté en la carpeta 'assets'.")

    # Marco principal dividido en secciones
    frame_datos = Frame(ventana, padx=10, pady=10, bg="#f0f0f0")
    frame_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_grafico = Frame(ventana, padx=10, pady=10, bg="white")
    frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Variables
    tipo_inversion = tk.StringVar(value="compuesto")
    entrada_monto = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_tasa = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_plazo = tk.Entry(frame_datos, font=("Arial", 12))

    # Crear elementos para ingresar datos
    tk.Label(frame_datos, text="Selecciona el tipo de inversión:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Interés Compuesto", variable=tipo_inversion, value="compuesto", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Interés Simple", variable=tipo_inversion, value="simple", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Aportaciones Periódicas", variable=tipo_inversion, value="periodicas", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Simulación Monte Carlo", variable=tipo_inversion, value="montecarlo", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")

    tk.Label(frame_datos, text="Monto inicial (S/):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_monto.pack(fill=tk.X, pady=5)
    tk.Label(frame_datos, text="Tasa de interés (%):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_tasa.pack(fill=tk.X, pady=5)
    tk.Label(frame_datos, text="Plazo (años):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_plazo.pack(fill=tk.X, pady=5)

    # Función para calcular y actualizar el gráfico
    def calcular_y_graficar():
        try:
            # Recuperar datos
            monto = float(entrada_monto.get())
            tasa = obtener_tasa_interes_actual()  # Obtener tasa de interés actual
            plazo = int(entrada_plazo.get())

            # Calcular resultados
            if tipo_inversion.get() == "compuesto":
                resultado = calcular_interes_compuesto(monto, tasa, plazo)
            elif tipo_inversion.get() == "simple":
                resultado = calcular_interes_simple(monto, tasa, plazo)
            elif tipo_inversion.get() == "periodicas":
                resultado = calcular_aportaciones_periodicas(monto, tasa, plazo)
            elif tipo_inversion.get() == "montecarlo":
                resultados = simulacion_monte_carlo(monto, tasa, plazo)
                messagebox.showinfo("Resultado", f"Capital final promedio: S/ {np.mean(resultados):.2f}")
                mostrar_grafico_monte_carlo(resultados)
                return

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

    def mostrar_grafico_monte_carlo(resultados):
        figure = plt.Figure(figsize=(6, 5), dpi=100)
        ax = figure.add_subplot(111)
        ax.hist(resultados, bins=50, alpha=0.75)
        ax.set_title("Distribución de Resultados de Monte Carlo")
        ax.set_xlabel("Capital Final (S/)")
        ax.set_ylabel("Frecuencia")
        for widget in frame_grafico.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(figure, frame_grafico)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    # Botones
    tk.Button(frame_datos, text="Calcular y Graficar", command=calcular_y_graficar, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10, fill=tk.X)

    # Agregar nuevo frame para información del mercado
    frame_mercado = Frame(ventana, padx=10, pady=10, bg="#f0f0f0")
    frame_mercado.pack(side=tk.BOTTOM, fill=tk.X)
    
    datos_peru = APIsFinancierasPeru()
    
    def actualizar_datos_mercado():
        try:
            tasa_ref = datos_peru.obtener_tasa_referencia_bcrp()
            inflacion = datos_peru.obtener_inflacion_anual()
            tipo_cambio = datos_peru.obtener_tipo_cambio()
            
            if all(dato is None for dato in [tasa_ref, inflacion, tipo_cambio]):
                messagebox.showwarning("Advertencia", "No se pudieron obtener datos del BCRP")
                label_mercado.config(text="No hay datos disponibles")
            else:
                texto = ""
                if tasa_ref is not None:
                    texto += f"Tasa BCRP: {tasa_ref:.2f}% | "
                    entrada_tasa.delete(0, tk.END)
                    entrada_tasa.insert(0, str(tasa_ref))
                if inflacion is not None:
                    texto += f"Inflación: {inflacion:.2f}% | "
                if tipo_cambio is not None:
                    texto += f"Tipo de Cambio: S/ {tipo_cambio:.2f}"
                label_mercado.config(text=texto.strip(' | '))
        except Exception as e:
            messagebox.showerror("Error", f"Error en la actualización: {str(e)}")
            label_mercado.config(text="Error al obtener datos del mercado")
    
    label_mercado = tk.Label(frame_mercado, text="Cargando datos del mercado...", bg="#f0f0f0")
    label_mercado.pack(pady=5)
    
    # Botón para actualizar datos del mercado
    tk.Button(frame_mercado, text="Actualizar Datos", command=actualizar_datos_mercado).pack(pady=5)

    # Agregar botón para ver datos de acciones
    def mostrar_datos_acciones():
        try:
            # Crear una nueva ventana para mostrar datos de acciones
            ventana_acciones = tk.Toplevel()
            ventana_acciones.title("Datos de Acciones Peruanas")
            ventana_acciones.geometry("400x300")
            
            # Crear lista de acciones disponibles
            lista_acciones = ttk.Combobox(ventana_acciones, values=list(datos_peru.tickers_peru.keys()))
            lista_acciones.pack(pady=10)
            
            def actualizar_datos_accion():
                ticker = lista_acciones.get()
                datos = datos_peru.obtener_datos_acciones_peruanas(ticker)
                if datos is not None:
                    # Mostrar últimos precios
                    texto_info = f"Último precio: {datos['Close'][-1]:.2f}\n"
                    texto_info += f"Máximo (1 año): {datos['High'].max():.2f}\n"
                    texto_info += f"Mínimo (1 año): {datos['Low'].min():.2f}"
                    label_info_acciones.config(text=texto_info)
            
            tk.Button(ventana_acciones, text="Actualizar", command=actualizar_datos_accion).pack(pady=5)
            label_info_acciones = tk.Label(ventana_acciones, text="Seleccione una acción")
            label_info_acciones.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar datos de acciones: {str(e)}")
    
    # Agregar botón para ver acciones
    tk.Button(frame_mercado, text="Ver Acciones", command=mostrar_datos_acciones).pack(pady=5)
    
    # Inicializar la interfaz
    ventana.mainloop()


if __name__ == "__main__":
    inicializar_db()
    interfaz_grafica()
