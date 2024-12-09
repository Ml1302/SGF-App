import tkinter as tk
import matplotlib.pyplot as plt  # Asegurarse de importar matplotlib
from tkinter import messagebox, ttk, Frame, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH
from db import inicializar_db, guardar_simulacion, obtener_historial, guardar_financiamiento, obtener_financiamientos_guardados, eliminar_financiamiento  # Importar eliminar_financiamiento
from calculos import calcular_interes_simple, calcular_interes_compuesto, calcular_aportaciones_periodicas, calcular_amortizacion_aleman, calcular_amortizacion_frances, calcular_tir, analisis_sensibilidad
from PIL import Image, ImageTk
from apis import APIsFinancierasPeru
from exportacion import exportar_datos, generar_reporte_pdf
import sqlite3
from datetime import datetime
import requests
import numpy as np  # Asegurarse de importar numpy
from calculos import convertir_tasa  # Importar la función convertir_tasa


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

def visualizar_comparacion():
    """Función para visualizar la comparación de financiamientos."""
    financiamientos = obtener_financiamientos_guardados()
    if not financiamientos:
        messagebox.showinfo("Información", "No hay financiamientos para comparar.")
        return
    
    # Crear solo la lista de financiamientos sin gráficos
    ventana_comparacion = tk.Toplevel()
    ventana_comparacion.title("Comparación de Financiamientos")
    ventana_comparacion.geometry("900x600")
    
    # Marco para la lista de financiamientos
    frame_lista_comparacion = Frame(ventana_comparacion, padx=10, pady=10)
    frame_lista_comparacion.pack(fill=tk.BOTH, expand=True)
    
    # Crear Treeview para mostrar financiamientos
    columns = ("ID", "Tipo", "Monto", "Tasa", "Plazo", "TIR")
    tree_comparacion = ttk.Treeview(frame_lista_comparacion, columns=columns, show='headings')
    for col in columns:
        tree_comparacion.heading(col, text=col)
        tree_comparacion.column(col, anchor="center")
    tree_comparacion.pack(fill=tk.BOTH, expand=True)
    
    for fin in financiamientos:
        tree_comparacion.insert("", "end", values=(
            fin['id'],
            fin['tipo_amortizacion'].capitalize(),
            f"S/ {fin['monto']:.2f}",
            f"{fin['tasa']:.2f}%",  # Mostrar tasa convertida
            fin['plazo'],
            f"{fin['tir']:.6f}%"  # Mostrar TIR sin redondeo
        ))
    
    # Función para mostrar el cronograma de pagos en comparación
    def mostrar_cronograma_comparacion(event):
        seleccionado = tree_comparacion.selection()
        if seleccionado:
            item = tree_comparacion.item(seleccionado)
            fin_id = item['values'][0]
            tipo = item['values'][1].lower()
            monto = float(item['values'][2].replace('S/ ', ''))
            tasa = float(item['values'][3].replace('%', ''))
            plazo = int(item['values'][4])
            
            if tipo == "alemán":
                amortizaciones = calcular_amortizacion_aleman(monto, tasa, plazo)
            elif tipo == "francés":
                amortizaciones = calcular_amortizacion_frances(monto, tasa, plazo)
            else:
                amortizaciones = []
                messagebox.showwarning("Tipo de amortización", "Tipo de amortización desconocido.")
            
            # Crear ventana para cronograma
            ventana_cronograma = tk.Toplevel()
            ventana_cronograma.title(f"Cronograma de Pagos - Financiamiento {fin_id}")
            ventana_cronograma.geometry("600x400")
            
            columns_cronograma = ("Cuota", "Interés", "Amortización", "Saldo", "Total Cuota")
            tree_cronograma = ttk.Treeview(ventana_cronograma, columns=columns_cronograma, show='headings')
            for col in columns_cronograma:
                tree_cronograma.heading(col, text=col)
                tree_cronograma.column(col, anchor="center")
            tree_cronograma.pack(fill=tk.BOTH, expand=True)
            for idx, pago in enumerate(amortizaciones, 1):
                total_cuota = pago['interés'] + pago['principal']
                tree_cronograma.insert("", "end", values=(
                    idx,
                    f"S/ {pago['interés']:.2f}",
                    f"S/ {pago['principal']:.2f}",
                    f"S/ {pago['saldo']:.2f}",
                    f"S/ {total_cuota:.2f}"
                ))
    
    tree_comparacion.bind("<<TreeviewSelect>>", mostrar_cronograma_comparacion)

    # Agregar botón para eliminar financiamiento seleccionado
    ventana_comparacion.geometry("800x600")
    ventana_comparacion.configure(bg="#f0f0f0")

    # Agregar ícono y logo
    # ventana_comparacion.iconbitmap("assets/icon.ico")  # Comentar o eliminar esta línea si no tienes el archivo

    try:
        logo = Image.open("assets/logo.png")
        logo = logo.resize((200, 100), Image.LANCZOS)  # Reemplaza ANTIALIAS por LANCZOS
        logo = ImageTk.PhotoImage(logo)
        tk.Label(ventana_comparacion, image=logo, bg="#f0f0f0").pack(pady=10)
    except FileNotFoundError:
        print("No se pudo cargar el logo. Asegúrate de que el archivo 'logo.png' esté en la carpeta 'assets'.")

    # Función para eliminar financiamiento seleccionado
    def eliminar_financiamiento_seleccionado():
        seleccionado = tree_comparacion.selection()
        if seleccionado:
            item = tree_comparacion.item(seleccionado)
            fin_id = item['values'][0]
            eliminar_financiamiento(fin_id)
            messagebox.showinfo("Eliminado", "Financiamiento eliminado correctamente.")
        else:
            messagebox.showwarning("Seleccionar", "Por favor, selecciona un financiamiento para eliminar.")

    # Botón para eliminar financiamiento
    tk.Button(ventana_comparacion, text="Eliminar Seleccionado", command=eliminar_financiamiento_seleccionado).pack(pady=5)

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

    # Crear un Notebook para pestañas
    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Crear pestañas
    tab_inversiones = ttk.Frame(notebook)
    tab_financiamientos = ttk.Frame(notebook)
    tab_datos_mercado = ttk.Frame(notebook)
    tab_analisis = ttk.Frame(notebook)

    notebook.add(tab_inversiones, text="Inversiones")
    notebook.add(tab_financiamientos, text="Financiamientos")
    notebook.add(tab_datos_mercado, text="Datos del Mercado")
    notebook.add(tab_analisis, text="Análisis Avanzado")

    # Marco principal dividido en secciones
    frame_datos = Frame(tab_inversiones, padx=10, pady=10, bg="#f0f0f0")
    frame_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_grafico = Frame(tab_inversiones, padx=10, pady=10, bg="white")
    frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Variables
    tipo_inversion = tk.StringVar(value="compuesto")
    entrada_monto = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_tasa = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_plazo = tk.Entry(frame_datos, font=("Arial", 12))

    # Crear elementos para ingresar datos
    tk.Label(frame_datos, text="Selecciona el tipo de inversión:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # tk.Radiobutton(frame_datos, text="Interés Compuesto", variable=tipo_inversion, value="compuesto", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # tk.Radiobutton(frame_datos, text="Interés Simple", variable=tipo_inversion, value="simple", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # tk.Radiobutton(frame_datos, text="Aportaciones Periódicas", variable=tipo_inversion, value="periodicas", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # tk.Radiobutton(frame_datos, text="Simulación Monte Carlo", variable=tipo_inversion, value="montecarlo", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")

    # tk.Label(frame_datos, text="Monto inicial (S/):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # entrada_monto.pack(fill=tk.X, pady=5)
    # tk.Label(frame_datos, text="Tasa de interés (%):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # entrada_tasa.pack(fill=tk.X, pady=5)
    # tk.Label(frame_datos, text="Plazo (años):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    # entrada_plazo.pack(fill=tk.X, pady=5)

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
    # tk.Button(frame_datos, text="Calcular y Graficar", command=calcular_y_graficar, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10, fill=tk.X)

    # Agregar nuevo frame para información del mercado
    frame_mercado = Frame(tab_datos_mercado, padx=10, pady=10, bg="#f0f0f0")
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
                label_mercado.config(texto.strip(' | '))
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
    
    # Agregar sección para comparación de financiamientos
    # tk.Label(frame_datos, text="Agregar Opciones de Financiamiento:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w", pady=(20, 5))

    opciones_financiamiento = []
    
    def agregar_opcion():
        tipo = tipo_var.get()
        try:
            monto = float(entrada_fin_monto.get())
            tasa = float(entrada_fin_tasa.get())
            plazo = int(entrada_fin_plazo.get())
            unidad_t = unidad_tasa.get()
            unidad_p = unidad_plazo.get()

            # Definir periodos por año según unidad
            periodos_por_anno = {
                "Anual": 1, "Anuales": 1, "Año": 1, "Años": 1,
                "Semestral": 2, "Semestrales": 2, "Semestre": 2, "Semestres": 2,
                "Trimestral": 4, "Trimestrales": 4, "Trimestre": 4, "Trimestres": 4,
                "Bimestral": 6, "Bimestrales": 6, "Bimestre": 6, "Bimestres": 6,
                "Mensual": 12, "Mensuales": 12, "Mes": 12, "Meses": 12
            }

            # Obtener los periodos por año para la tasa y el plazo
            periodo_origen = periodos_por_anno.get(unidad_t, None)
            periodo_destino = periodos_por_anno.get(unidad_p, None)

            if periodo_origen is None:
                messagebox.showerror("Error", f"Unidad de tasa desconocida: {unidad_t}")
                return
            if periodo_destino is None:
                messagebox.showerror("Error", f"Unidad de plazo desconocida: {unidad_p}")
                return

            # Convertir tasa a formato decimal
            tasa_decimal = tasa / 100

            # Convertir la tasa utilizando la función convertir_tasa
            tasa_convertida_decimal = convertir_tasa(tasa_decimal, periodo_origen, periodo_destino)
            tasa_convertida = tasa_convertida_decimal * 100  # Volver a porcentaje

            # Calcular el total de períodos
            total_periodos = plazo * periodo_destino

            # Calcular amortización y TIR usando la tasa convertida y el número de periodos
            if tipo == "alemán":
                amort = calcular_amortizacion_aleman(monto, tasa_convertida, int(total_periodos))
            else:
                amort = calcular_amortizacion_frances(monto, tasa_convertida, int(total_periodos))

            flujos = [-monto] + [pago['cuota'] for pago in amort]
            tir = calcular_tir(flujos)

            # Guardar en la base de datos con la tasa convertida
            guardar_financiamiento(tipo, monto, tasa_convertida, int(total_periodos), tir)
            messagebox.showinfo("Éxito", f"Financiamiento agregado correctamente\nTasa convertida: {tasa_convertida:.4f}%")

            # Limpiar campos
            entrada_fin_monto.delete(0, tk.END)
            entrada_fin_tasa.delete(0, tk.END)
            entrada_fin_plazo.delete(0, tk.END)
            # Actualizar lista de opciones
            cargar_financiamientos()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores válidos para monto, tasa y plazo.")

    def cargar_financiamientos():
        # Limpiar el Treeview
        tree_financiamientos.delete(*tree_financiamientos.get_children())
        # Obtener financiamientos guardados
        financiamientos = obtener_financiamientos_guardados()
        for financiamiento in financiamientos:
            try:
                tree_financiamientos.insert("", "end", values=(
                    financiamiento['id'],
                    financiamiento['tipo_amortizacion'].capitalize(),
                    f"S/ {financiamiento['monto']:.2f}",
                    f"{financiamiento['tasa']:.2f}%",  # Aquí se muestra la tasa convertida
                    financiamiento['plazo'],
                    f"{financiamiento['tir']:.6f}%"  # Mostrar TIR sin redondeo
                ))
            except KeyError as e:
                print(f"Missing key in financiamiento data: {e}")
                # Manejar la clave faltante apropiadamente
                tree_financiamientos.insert("", "end", values=(
                    financiamiento.get('id', 'N/A'),
                    financiamiento.get('tipo_amortizacion', 'N/A').capitalize(),
                    f"S/ {financiamiento.get('monto', 0)::.2f}",
                    f"{financiamiento.get('tasa', 0)::.2f}%",
                    financiamientos.get('plazo', 'N/A'),
                    f"{financiamientos.get('tir', 0):.6f}%"  # Mostrar TIR sin redondeo
                ))
        # ...existing code...

    def eliminar_opcion():
        seleccion = tree_financiamientos.selection()  # Reemplazar 'lista_opciones' con 'tree_financiamientos'
        if seleccion:
            item = tree_financiamientos.item(seleccion)
            fin_id = int(item['values'][0])  # Asumiendo que 'id' es el primer valor
            eliminar_financiamiento(fin_id)
            messagebox.showinfo("Información", "Financiamiento eliminado.")
            cargar_financiamientos()
        else:
            messagebox.showwarning("Advertencia", "Selecciona un financiamiento para eliminar.")

    tk.Button(frame_datos, text="Visualizar Comparación", command=visualizar_comparacion).pack(pady=10, fill=tk.X)

    # Declarar variables para opciones de financiamiento
    tipo_var = tk.StringVar(value="alemán")
    entrada_fin_monto = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_fin_tasa = tk.Entry(frame_datos, font=("Arial", 12))
    entrada_fin_plazo = tk.Entry(frame_datos, font=("Arial", 12))
    
    # Variables para unidades
    unidad_tasa = tk.StringVar(value="Anual")
    unidad_plazo = tk.StringVar(value="Meses")
    
    # Crear elementos para ingresar financiamiento
    tk.Label(frame_datos, text="Tipo de Amortización:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Alemán", variable=tipo_var, value="alemán", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Francés", variable=tipo_var, value="frances", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    
    tk.Label(frame_datos, text="Monto (S/):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_fin_monto.pack(fill=tk.X, pady=5)
    
    tk.Label(frame_datos, text="Tasa (%) :", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_fin_tasa.pack(fill=tk.X, pady=5)
    
    # Añadir selección de unidad para la tasa
    tk.Label(frame_datos, text="Unidad de Tasa de Interés:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    opciones_unidad_tasa = ["Anual", "Semestral", "Trimestral", "Bimestral", "Mensual"]
    combobox_unidad_tasa = ttk.Combobox(frame_datos, textvariable=unidad_tasa, values=opciones_unidad_tasa, state="readonly")
    combobox_unidad_tasa.pack(fill=tk.X, pady=5)
    
    tk.Label(frame_datos, text="Plazo (cantidad):", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    entrada_fin_plazo.pack(fill=tk.X, pady=5)
    
    # Añadir selección de unidad para el plazo
    tk.Label(frame_datos, text="Unidad de Plazo:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w")
    opciones_unidad_plazo = ["Anual", "Semestral", "Trimestral", "Bimestral", "Mensual"]
    combobox_unidad_plazo = ttk.Combobox(frame_datos, textvariable=unidad_plazo, values=opciones_unidad_plazo, state="readonly")
    combobox_unidad_plazo.pack(fill=tk.X, pady=5)

    # Función generalizada para convertir tasas de interés
    def convertir_tasa(tasa_original, periodo_origen, periodo_destino):
        """
        Convierte una tasa de interés de un periodo a otro.
        
        Parámetros:
        - tasa_original: Tasa de interés en formato decimal (por ejemplo, 0.12 para 12%).
        - periodo_origen: Número de periodos por unidad de tiempo original (por ejemplo, 1 para anual).
        - periodo_destino: Número de periodos por unidad de tiempo destino (por ejemplo, 12 para mensual).
        
        Retorna:
        - Tasa convertida en formato decimal.
        """
        tasa_convertida = (1 + tasa_original) ** (periodo_origen / periodo_destino) - 1
        return tasa_convertida

    # Agregar botón para agregar financiamiento
    tk.Button(frame_datos, text="Agregar Financiamiento", command=agregar_opcion, font=("Arial", 12), bg="#2196F3", fg="white").pack(pady=10, fill=tk.X)

    # Agregar frame para análisis avanzado
    frame_analisis = Frame(tab_analisis, padx=10, pady=10, bg="#f0f0f0")
    frame_analisis.pack(side=tk.BOTTOM, fill=tk.X)

    def realizar_analisis_sensibilidad():
        try:
            monto = float(entrada_monto.get())
            tasa = float(entrada_tasa.get())
            plazo = int(entrada_plazo.get())
            
            resultados = analisis_sensibilidad(monto, tasa, plazo)
            mostrar_grafico_sensibilidad(resultados)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos")

    def exportar_resultados():
        try:
            datos = obtener_historial()
            nombre_archivo = f"resultados_financieros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            exportar_datos(datos, nombre_archivo)
            messagebox.showinfo("Éxito", f"Datos exportados a {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def mostrar_grafico_sensibilidad(resultados):
        figure = plt.Figure(figsize=(6, 4))
        ax = figure.add_subplot(111)
        tasas = [r['tasa'] for r in resultados]
        vans = [r['van'] for r in resultados]
        ax.plot(tasas, vans, marker='o')
        ax.set_title("Análisis de Sensibilidad")
        ax.set_xlabel("Tasa de Interés (%)")
        ax.set_ylabel("VAN")
        ax.grid(True)
        
        # Mostrar en el frame_grafico
        for widget in frame_grafico.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(figure, frame_grafico)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    # Agregar botones para nuevas funcionalidades
    tk.Button(frame_analisis, text="Análisis de Sensibilidad", 
              command=realizar_analisis_sensibilidad).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_analisis, text="Exportar Resultados", 
              command=exportar_resultados).pack(side=tk.LEFT, padx=5)

    # Agregar sección para listar financiamientos en la pestaña "Financiamientos"
    frame_list_financiamientos = Frame(tab_financiamientos, padx=10, pady=10, bg="#f0f0f0")
    frame_list_financiamientos.pack(fill=tk.BOTH, expand=True)

    # Crear Treeview para mostrar financiamientos, añadiendo la columna "Eliminar"
    columns = ("ID", "Tipo", "Monto", "Tasa", "Plazo (meses)", "TIR", "Eliminar")
    tree_financiamientos = ttk.Treeview(frame_list_financiamientos, columns=columns, show='headings')

    for col in columns:
        tree_financiamientos.heading(col, text=col)
        tree_financiamientos.column(col, anchor="center")
        if col == "Eliminar":
            tree_financiamientos.column(col, width=80)

    tree_financiamientos.pack(fill=tk.BOTH, expand=True)

    # Definir la función 'on_double_click' antes de usarla
    def on_double_click(event):
        item = tree_financiamientos.identify_row(event.y)
        column = tree_financiamientos.identify_column(event.x)
        if column == '#7':  # Columna "Eliminar" es la séptima columna
            if item:
                financiamiento_id = tree_financiamientos.item(item)['values'][0]
                eliminar_financiamiento_por_id(financiamiento_id)

    # Asociar evento de doble clic para detectar clics en "Eliminar"
    tree_financiamientos.bind("<Double-1>", on_double_click)

    # Función para eliminar financiamiento por ID
    def eliminar_financiamiento_por_id(financiamiento_id):
        # Confirmar eliminación
        confirmar = messagebox.askyesno("Confirmar", "¿Deseas eliminar este financiamiento?")
        if confirmar:
            eliminar_financiamiento(financiamiento_id)  # Eliminar de la base de datos
            cargar_financiamientos()  # Actualizar la lista
            messagebox.showinfo("Éxito", "El financiamiento ha sido eliminado.")

    # Función para manejar el clic en la celda "Eliminar"
    def on_double_click(event):
        item = tree_financiamientos.identify_row(event.y)
        column = tree_financiamientos.identify_column(event.x)
        if column == '#7':  # Columna "Eliminar" es la séptima columna
            if item:
                financiamiento_id = tree_financiamientos.item(item)['values'][0]
                eliminar_financiamiento_por_id(financiamiento_id)

    # Función para cargar financiamientos desde la base de datos
    def cargar_financiamientos():
        # Limpiar el Treeview
        for item in tree_financiamientos.get_children():
            tree_financiamientos.delete(item)
        # Obtener financiamientos guardados
        financiamientos = obtener_financiamientos_guardados()
        for financiamiento in financiamientos:
            try:
                tree_financiamientos.insert("", "end", values=(
                    financiamiento['id'],
                    financiamiento['tipo_amortizacion'].capitalize(),
                    f"S/ {financiamiento['monto']:.2f}",
                    f"{financiamiento['tasa']:.2f}%",  # Mostrar tasa convertida
                    financiamiento['plazo'],
                    f"{financiamiento['tir']:.6f}%",
                    "Eliminar"  # Texto en la columna "Eliminar"
                ))
            except KeyError as e:
                print(f"Missing key in financiamiento data: {e}")
                # Manejar la clave faltante apropiadamente
                tree_financiamientos.insert("", "end", values=(
                    financiamiento.get('id', 'N/A'),
                    financiamiento.get('tipo_amortizacion', 'N/A').capitalize(),
                    f"S/ {financiamiento.get('monto', 0):.2f}",
                    f"{financiamiento.get('tasa', 0):.2f}%",
                    financiamiento.get('plazo', 'N/A'),
                    f"{financiamiento.get('tir', 0):.6f}%",
                    "Eliminar"  # Texto en la columna "Eliminar"
                ))

    # Cargar financiamientos al iniciar la interfaz gráfica
    cargar_financiamientos()

    def eliminar_financiamiento_seleccionado():
        seleccionado = tree_financiamientos.selection()
        if seleccionado:
            item = tree_financiamientos.item(seleccionado)
            financiamiento_id = item['values'][0]

            # Confirmar eliminación
            confirmar = messagebox.askyesno("Confirmar", "¿Deseas eliminar este financiamiento?")
            if confirmar:
                eliminar_financiamiento(financiamiento_id)  # Eliminar de la base de datos
                cargar_financiamientos()  # Actualizar la lista
                messagebox.showinfo("Éxito", "El financiamiento ha sido eliminado.")
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un financiamiento para eliminar.")

    # Función para mostrar el cronograma de pagos
    def mostrar_cronograma():
        seleccionado = tree_financiamientos.selection()
        if seleccionado:
            item = tree_financiamientos.item(seleccionado)
            fin_id = item['values'][0]
            tipo = item['values'][1].lower()
            monto = float(item['values'][2].replace('S/ ', ''))
            tasa = float(item['values'][3].replace('%', ''))
            plazo = int(item['values'][4])
            
            if tipo == "alemán":
                amortizaciones = calcular_amortizacion_aleman(monto, tasa, plazo)
            elif tipo == "francés":
                amortizaciones = calcular_amortizacion_frances(monto, tasa, plazo)
            else:
                messagebox.showerror("Error", "Tipo de amortización desconocido.")
                return
            
            # Crear ventana para cronograma
            ventana_cronograma = tk.Toplevel()
            ventana_cronograma.title(f"Cronograma de Pagos - Financiamiento {fin_id}")
            ventana_cronograma.geometry("600x400")
            
            columns_cronograma = ("Cuota", "Interés", "Amortización", "Saldo")
            tree_cronograma = ttk.Treeview(ventana_cronograma, columns=columns_cronograma, show='headings')
            for col in columns_cronograma:
                tree_cronograma.heading(col, text=col)
                tree_cronograma.column(col, anchor="center")
            tree_cronograma.pack(fill=tk.BOTH, expand=True)
            for idx, pago in enumerate(amortizaciones, 1):
                tree_cronograma.insert("", "end", values=(
                    idx,
                    f"S/ {pago['interés']:.2f}",
                    f"S/ {pago['principal']:.2f}",
                    f"S/ {pago['saldo']:.2f}"
                ))

    # Vincular el evento de selección al Treeview
    tree_financiamientos.bind("<<TreeviewSelect>>", mostrar_cronograma)

    # Inicializar la interfaz
    ventana.mainloop()


if __name__=="__main__":
    inicializar_db()
    interfaz_grafica()
