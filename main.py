import tkinter as tk
import matplotlib.pyplot as plt  # Asegurarse de importar matplotlib
from tkinter import messagebox, ttk, Frame, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH
from db import inicializar_db, guardar_simulacion, obtener_historial, guardar_financiamiento, obtener_financiamientos_guardados, eliminar_financiamiento  # Importar eliminar_financiamiento
from PIL import Image, ImageTk
from apis import APIsFinancierasPeru
from exportacion import exportar_datos, generar_reporte_pdf
import sqlite3
from datetime import datetime
import requests
import numpy as np  # Asegurarse de importar numpy
from calculos import * # Importar la función convertir_tasa
from graficos import *
from tkinter import filedialog
import csv
import pandas as pd
from calculos import calcular_amortizacion_aleman, calcular_amortizacion_frances, convertir_tasa, calcular_tir  # Importar las funciones necesarias
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
    
    # Crear Treeview para mostrar financiamientos, añadiendo la columna "Eliminar"
    columns = ("ID", "Tipo", "Monto", "Tasa", "Plazo", "TIR", "Eliminar")
    tree_comparacion = ttk.Treeview(frame_lista_comparacion, columns=columns, show='headings')
    for col in columns:
        tree_comparacion.heading(col, text=col)
        tree_comparacion.column(col, anchor="center")
        if col == "Eliminar":
            tree_comparacion.column(col, width=100)  # Ajustar ancho de la columna Eliminar
    
    tree_comparacion.pack(side=LEFT, fill=tk.BOTH, expand=True)
    
    # Scrollbar para el Treeview
    scrollbar = ttk.Scrollbar(frame_lista_comparacion, orient=VERTICAL, command=tree_comparacion.yview)
    scrollbar.pack(side=LEFT, fill=Y)
    tree_comparacion.configure(yscrollcommand=scrollbar.set)
    
    for fin in financiamientos:
        tree_comparacion.insert("", "end", values=(
            fin['id'],
            fin['tipo_amortizacion'].capitalize(),
            f"S/ {fin['monto']:.2f}",
            f"{fin['tasa']:.2f}%",  # Mostrar tasa convertida
            fin['plazo'],
            f"{fin['tir']:.6f}%",
            "Eliminar"  # Texto para la columna Eliminar
        ))
    
    # Función para mostrar el cronograma con doble clic
    def on_double_click(event):
        item_id = tree_comparacion.selection()
        if item_id:
            item = tree_comparacion.item(item_id)
            financiamiento_id = item['values'][0]
            financiamiento = next((f for f in obtener_financiamientos_guardados() if f['id'] == financiamiento_id), None)
            
            if not financiamiento:
                return
            
            # ...existing code to mostrar_cronograma...
            mostrar_cronograma_financiamiento(financiamiento)
    
    # Función para eliminar financiamiento haciendo clic en la columna "Eliminar"
    def on_single_click(event):
        region = tree_comparacion.identify("region", event.x, event.y)
        column = tree_comparacion.identify_column(event.x)
        if region == "cell" and column == "#7":  # La columna "Eliminar" es la #7
            item = tree_comparacion.identify_row(event.y)
            if item:
                fin_id = tree_comparacion.item(item)['values'][0]
                confirmar = messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que deseas eliminar este financiamiento?")
                if confirmar:
                    eliminar_financiamiento(fin_id)
                    messagebox.showinfo("Eliminado", "Financiamiento eliminado correctamente.")
                    cargar_financiamientos_comparacion(tree_comparacion)
    
    tree_comparacion.bind("<Double-1>", on_double_click)
    tree_comparacion.bind("<Button-1>", on_single_click)  # Para el clic en "Eliminar"

    # ...existing code...
    
    # Eliminar el botón de eliminar seleccionado
    # ...existing code...
    # Por ejemplo, comentar o eliminar las siguientes líneas si existen:
    # def eliminar_financiamiento_seleccionado():
    #     # ...existing code...
    
    # btn_eliminar = tk.Button(frame_botones, text="Eliminar Seleccionado", command=eliminar_financiamiento_seleccionado, bg="#e74c3c", fg="white")
    # btn_eliminar.pack(pady=5, fill=tk.X)
    
    # ...existing code...
    
    # Función para mostrar el cronograma de un financiamiento
    def mostrar_cronograma_financiamiento(financiamiento):
        monto = financiamiento['monto']
        tasa = financiamiento['tasa']
        plazo = financiamiento['plazo']
        tipo_amortizacion = financiamiento['tipo_amortizacion']
        portes = financiamiento.get('portes', 0)
        mantenimiento = financiamiento.get('mantenimiento', 0)
        desgravamen = financiamiento.get('desgravamen', 0)
        
        # Calcular el cronograma según el tipo de amortización
        if tipo_amortizacion.lower() == 'alemán':
            cronograma = calcular_amortizacion_aleman(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        elif tipo_amortizacion.lower() == 'frances':
            cronograma = calcular_amortizacion_frances(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        else:
            messagebox.showerror("Error", f"Tipo de amortización desconocido: {tipo_amortizacion}")
            return

        # Mostrar el cronograma en una nueva ventana
        ventana_cronograma = tk.Toplevel()
        ventana_cronograma.title(f"Cronograma de {tipo_amortizacion.capitalize()}")
        ventana_cronograma.geometry("1200x600")  # Ventana más grande

        columns = ("Periodo", "Cuota", "Interés", "Amortización", "Portes", "Mantenimiento", "Desgravamen", "Cuota Total", "Saldo")
        tree_cronograma = ttk.Treeview(ventana_cronograma, columns=columns, show='headings')
        
        # Configurar anchos de columna específicos
        column_widths = {
            "Periodo": 70,
            "Cuota": 100,
            "Interés": 100,
            "Amortización": 100,
            "Portes": 100,
            "Mantenimiento": 100,
            "Desgravamen": 100,
            "Cuota Total": 100,
            "Saldo": 100
        }
        
        for col in columns:
            tree_cronograma.heading(col, text=col)
            tree_cronograma.column(col, anchor="center", width=column_widths[col])

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(ventana_cronograma, orient="vertical", command=tree_cronograma.yview)
        scrollbar.pack(side="right", fill="y")
        tree_cronograma.configure(yscrollcommand=scrollbar.set)
        
        tree_cronograma.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Insertar datos en el Treeview
        for i, fila in enumerate(cronograma, 1):
            tree_cronograma.insert("", "end", values=(
                i,
                f"S/ {fila['cuota']:.2f}",
                f"S/ {fila['interés']:.2f}",
                f"S/ {fila['principal']:.2f}",
                f"S/ {fila['portes']:.2f}",
                f"S/ {fila['mantenimiento']:.2f}",
                f"S/ {fila['desgravamen']:.2f}",
                f"S/ {fila['cuota_total']:.2f}",
                f"S/ {fila['saldo']:.2f}"
            ))
    
    # Función para cargar financiamientos en la comparación
    def cargar_financiamientos_comparacion(tree):
        tree.delete(*tree.get_children())
        financiamientos = obtener_financiamientos_guardados()
        for fin in financiamientos:
            tree.insert("", "end", values=(
                fin['id'],
                fin['tipo_amortizacion'].capitalize(),
                f"S/ {fin['monto']:.2f}",
                f"{fin['tasa']:.2f}%",
                fin['plazo'],
                f"{fin['tir']:.6f}%",
                "Eliminar"
            ))

def interfaz_grafica():
    global tree_financiamientos  # Declare as global at the start of the function
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

    notebook.add(tab_inversiones, text="Opciones de financiamiento")
    notebook.add(tab_financiamientos, text="Historial de financimaientos")
    notebook.add(tab_analisis, text="Análisis avanzado de financiamientos")
    notebook.add(tab_datos_mercado, text="Inversión en acciones")
    

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
    tk.Label(frame_datos, text="Rellena el formulario con el financiamiento que deseas analizar:", bg="#f0f0f0").pack(anchor="w")

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

    # Botones
    # tk.Button(frame_datos, text="Calcular y Graficar", command=calcular_y_graficar, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10, fill=tk.X)

    # Agregar nuevo frame para información del mercado
    frame_mercado = Frame(tab_datos_mercado, padx=10, pady=10, bg="#f0f0f0")
    frame_mercado.pack(side=tk.BOTTOM, fill=tk.X)
    
    datos_peru = APIsFinancierasPeru()
     
    # Lista de acciones
    tk.Label(tab_datos_mercado, text="Seleccione una acción:").pack(pady=5)
    lista_acciones = ttk.Combobox(tab_datos_mercado, values=list(datos_peru.tickers_peru.keys()))
    lista_acciones.pack(pady=5)

    # Mostrar datos históricos
    label_historial = tk.Label(tab_datos_mercado, text="Historial de la acción:")
    label_historial.pack(pady=5)
    texto_historial = tk.Text(tab_datos_mercado, height=10, width=60)
    texto_historial.pack(pady=5)

    def actualizar_historial():
        ticker = lista_acciones.get()
        if not ticker:
            messagebox.showerror("Error", "Seleccione una acción.")
            return
        
        datos = datos_peru.obtener_datos_acciones_peruanas(ticker)
        if datos is not None:
            texto_historial.delete("1.0", tk.END)
            texto_historial.insert(tk.END, f"Último precio: {datos['Close'][-1]:.2f}\n")
            texto_historial.insert(tk.END, f"Máximo (1 año): {datos['High'].max():.2f}\n")
            texto_historial.insert(tk.END, f"Mínimo (1 año): {datos['Low'].min():.2f}\n")
        else:
            messagebox.showerror("Error", "No se pudo obtener los datos.")

    tk.Button(tab_datos_mercado, text="Actualizar", command=actualizar_historial).pack(pady=5)

    # Simulación Monte Carlo
    tk.Label(tab_datos_mercado, text="Parámetros para Análisis de Riesgo:").pack(pady=5)
    tk.Label(tab_datos_mercado, text="Tasa de Interés (%):").pack()
    entry_tasa = tk.Entry(tab_datos_mercado)
    entry_tasa.pack(pady=5)

    tk.Label(tab_datos_mercado, text="Días de Simulación:").pack()
    entry_dias = tk.Entry(tab_datos_mercado)
    entry_dias.pack(pady=5)

    tk.Label(tab_datos_mercado, text="Número de Simulaciones:").pack()
    entry_simulaciones = tk.Entry(tab_datos_mercado)
    entry_simulaciones.pack(pady=5)

    def realizar_analisis():
        try:
            ticker = lista_acciones.get()
            if not ticker:
                raise ValueError("Seleccione una acción.")
            
            tasa_interes = float(entry_tasa.get())
            dias_simulacion = int(entry_dias.get())
            num_simulaciones = int(entry_simulaciones.get())

            datos = datos_peru.obtener_datos_acciones_peruanas(ticker)
            if datos is None:
                raise ValueError("No se pudo obtener los datos históricos para la acción seleccionada.")

            precio_inicial = datos['Close'][-1]
            resultados = simulacion_montecarlo(precio_inicial, tasa_interes / 100, dias_simulacion, num_simulaciones)
            resumen = analisis_riesgo_simulacion(resultados)

            mostrar_grafico_monte_carlo(resultados)
            messagebox.showinfo("Resultados", f"Promedio: {resumen['capital_final_promedio']:.2f}\n"
                                            f"Máximo: {resumen['capital_final_maximo']:.2f}\n"
                                            f"Mínimo: {resumen['capital_final_minimo']:.2f}\n"
                                            f"Desviación estándar: {resumen['desviacion_estandar']:.2f}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    tk.Button(tab_datos_mercado, text="Realizar Análisis", command=realizar_analisis).pack(pady=10)

    # Mantener funcionalidades originales en "Inversiones", "Financiamientos" y "Análisis Avanzados"
    tk.Label(tab_financiamientos, text="Funcionalidades de Financiamientos aquí.").pack(pady=20)
    tk.Label(tab_analisis, text="Funcionalidades de Análisis Avanzados aquí.").pack(pady=20)
    # Agregar sección para comparación de financiamientos
    # tk.Label(frame_datos, text="Agregar Opciones de Financiamiento:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor="w", pady=(20, 5))

    opciones_financiamiento = []
    
    def agregar_opcion():
        tipo = tipo_var.get()
        try:
            monto = float(entrada_fin_monto.get())
            tasa = float(entrada_fin_tasa.get())
            plazo = int(entrada_fin_plazo.get())
            portes = float(entrada_portes.get()) if entrada_portes.get() else 0
            mantenimiento = float(entrada_mantenimiento.get()) if entrada_mantenimiento.get() else 0
            desgravamen = float(entrada_desgravamen.get()) if entrada_desgravamen.get() else 0

            # Convertir la tasa y el plazo a unidades mensuales si es necesario
            tasa_unidad = unidad_tasa.get()
            plazo_unidad = unidad_plazo.get()

            tasa_periodos = {'Anual':1, 'Semestral':2, 'Trimestral':4, 'Bimestral':6, 'Mensual':12}
            periodo_origen = tasa_periodos[tasa_unidad]
            periodo_destino = tasa_periodos[plazo_unidad]

            tasa_convertida = convertir_tasa(tasa/100, periodo_origen, periodo_destino) * 100  # Convertir a porcentaje

            # Calcular cronograma según el tipo de amortización
            if tipo == 'alemán':
                cronograma = calcular_amortizacion_aleman(monto, tasa_convertida, plazo, portes, mantenimiento, desgravamen)
            elif tipo == 'frances':
                cronograma = calcular_amortizacion_frances(monto, tasa_convertida, plazo, portes, mantenimiento, desgravamen)
            else:
                messagebox.showerror("Error", "Tipo de amortización no reconocido.")
                return

            # Calcular TIR incluyendo las cuotas adicionales
            flujos = [-monto]  # Préstamo como negativo
            for fila in cronograma:
                flujos.append(fila['cuota_total'])  # Asegurarse de que 'cuota_total' sea positiva
            
            # Opcional: Imprimir los flujos para depuración
            # print(f"Flujos de caja para TIR: {flujos}")
            
            tir = calcular_tir(flujos)
            if tir is None or not isinstance(tir, (int, float)):
                tir = 0  # Asignar valor por defecto si la TIR es inválida
            # Guardar el financiamiento en la base de datos (modifique según su implementación)
            guardar_financiamiento(tipo, monto, tasa_convertida, plazo, tir, portes, mantenimiento, desgravamen)
            messagebox.showinfo("Éxito", "Financiamiento agregado correctamente.")
            cargar_financiamientos()
        except ValueError as e:
            messagebox.showerror("Error", f"Por favor, ingrese valores numéricos válidos. Detalle: {e}")

    def cargar_financiamientos():
        # Limpiar el Treeview
        tree_financiamientos.delete(*tree_financiamientos.get_children())
        # Obtener financiamientos guardados
        financiamientos = obtener_financiamientos_guardados()
        for financiamiento in financiamientos:
            tree_financiamientos.insert("", "end", values=(
                financiamiento['id'],
                financiamiento['tipo_amortizacion'].capitalize(),
                f"S/ {financiamiento['monto']:.2f}",
                f"{financiamiento['tasa']:.2f}%",
                financiamiento['plazo'],
                f"{financiamiento['tir']:.6f}%"
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

    # Declarar variables para opciones de financiamiento
    tipo_var = tk.StringVar(value="alemán")
    entrada_fin_monto = tk.Entry(frame_datos)
    entrada_fin_tasa = tk.Entry(frame_datos)
    entrada_fin_plazo = tk.Entry(frame_datos)
    
    # Variables para unidades
    unidad_tasa = tk.StringVar(value="Anual")
    unidad_plazo = tk.StringVar(value="Mensual")  # Cambiar 'Meses' a 'Mensual'
    
    # Crear elementos para ingresar financiamiento
    tk.Label(frame_datos, text="Tipo de Amortización:", bg="#f0f0f0").pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Alemán", variable=tipo_var, value="alemán", bg="#f0f0f0").pack(anchor="w")
    tk.Radiobutton(frame_datos, text="Francés", variable=tipo_var, value="frances", bg="#f0f0f0").pack(anchor="w")
    
    tk.Label(frame_datos, text="Monto (S/):", bg="#f0f0f0").pack(anchor="w")
    entrada_fin_monto.pack(fill=tk.X, pady=5)
    
    tk.Label(frame_datos, text="Tasa (%) :", bg="#f0f0f0").pack(anchor="w")
    entrada_fin_tasa.pack(fill=tk.X, pady=5)
    
    # Añadir selección de unidad para la tasa
    tk.Label(frame_datos, text="Unidad de Tasa de Interés:", bg="#f0f0f0").pack(anchor="w")
    opciones_unidad_tasa = ["Anual", "Semestral", "Trimestral", "Bimestral", "Mensual"]
    combobox_unidad_tasa = ttk.Combobox(frame_datos, textvariable=unidad_tasa, values=opciones_unidad_tasa, state="readonly")
    combobox_unidad_tasa.pack(fill=tk.X, pady=5)
    
    tk.Label(frame_datos, text="Plazo (cantidad):", bg="#f0f0f0").pack(anchor="w")
    entrada_fin_plazo.pack(fill=tk.X, pady=5)
    
    # Añadir selección de unidad para el plazo
    tk.Label(frame_datos, text="Unidad de Plazo:", bg="#f0f0f0").pack(anchor="w")
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

    # Añadir los campos de entrada para Portes, Mantenimiento y Desgravamen
    tk.Label(frame_datos, text="Portes (S/):", bg="#f0f0f0").pack(anchor="w")
    entrada_portes = tk.Entry(frame_datos)
    entrada_portes.pack(fill=tk.X, pady=5)

    tk.Label(frame_datos, text="Mantenimiento (S/):", bg="#f0f0f0").pack(anchor="w")
    entrada_mantenimiento = tk.Entry(frame_datos)
    entrada_mantenimiento.pack(fill=tk.X, pady=5)

    tk.Label(frame_datos, text="Desgravamen (S/):", bg="#f0f0f0").pack(anchor="w")
    entrada_desgravamen = tk.Entry(frame_datos)
    entrada_desgravamen.pack(fill=tk.X, pady=5)

    # Asegurarse de que el botón "Agregar Financiamiento" está correctamente configurado
    tk.Button(frame_datos, text="Agregar Financiamiento", command=agregar_opcion).pack(pady=10, fill=tk.X)

    tk.Button(frame_datos, text="Visualizar Comparación", command=visualizar_comparacion).pack(pady=10, fill=tk.X)

    # Agregar frame para análisis avanzado
    frame_analisis = Frame(tab_analisis, padx=10, pady=10, bg="#f0f0f0")
    frame_analisis.pack(side=tk.BOTTOM, fill=tk.X)

    def realizar_analisis_sensibilidad():
        try:
            # Seleccionar un financiamiento del historial en tree_analisis
            seleccionado = tree_analisis.selection()
            if not seleccionado:
                raise ValueError("Por favor, selecciona un financiamiento del historial.")

            # Obtener datos del financiamiento seleccionado
            item = tree_analisis.item(seleccionado[0])  # Accede al primer elemento seleccionado
            valores = item['values']  # Valores del elemento

            # Extraer información necesaria
            monto = float(str(valores[2]).replace('S/ ', ''))
            tasa = float(str(valores[3]).replace('%', ''))
            plazo = int(valores[4])

            # Ejecutar el análisis de sensibilidad
            resultados = analisis_sensibilidad(monto, tasa, plazo)

            # Mostrar el gráfico en una ventana emergente
            mostrar_grafico_sensibilidad_emergente(resultados)

        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos seleccionados: {e}")
        except IndexError:
            messagebox.showerror("Error", "No se pudo acceder a los datos del financiamiento seleccionado.")

    # Crear Treeview para análisis avanzado
    frame_analisis_lista = Frame(tab_analisis, padx=10, pady=10, bg="#f0f0f0")
    frame_analisis_lista.pack(fill=tk.BOTH, expand=True)

    columns = ("ID", "Tipo", "Monto", "Tasa", "Plazo")
    tree_analisis = ttk.Treeview(frame_analisis_lista, columns=columns, show='headings')
    for col in columns:
        tree_analisis.heading(col, text=col)
        tree_analisis.column(col, anchor="center")
    tree_analisis.pack(fill=tk.BOTH, expand=True)

    def cargar_datos_analisis():
        """Cargar financiamientos al Treeview de análisis."""
        # Limpiar el Treeview
        tree_analisis.delete(*tree_analisis.get_children())
        financiamientos = obtener_financiamientos_guardados()
        for fin in financiamientos:
            tree_analisis.insert("", "end", values=(
                fin['id'],
                fin['tipo_amortizacion'].capitalize(),
                f"S/ {fin['monto']:.2f}",
                f"{fin['tasa']:.2f}%",
                fin['plazo']
            ))

    # Cargar financiamientos al iniciar
    cargar_datos_analisis()

    # Agregar botones para nuevas funcionalidades
    tk.Button(frame_analisis, text="Análisis de Sensibilidad", 
              command=realizar_analisis_sensibilidad).pack(side=tk.LEFT, padx=5)

    # Aqui todo sobre montecarlos
    def realizar_analisis_montecarlo():
        try:
            # Obtener datos del financiamiento seleccionado
            seleccionado = tree_analisis.selection()
            if not seleccionado:
                raise ValueError("Por favor, selecciona un financiamiento del historial.")

            # Obtener datos del financiamiento seleccionado
            item = tree_analisis.item(seleccionado[0])
            valores = item['values']

            monto_inicial = float(str(valores[2]).replace('S/ ', ''))
            tasa_media = float(str(valores[3]).replace('%', '')) / 100  # Convertir a decimal
            plazo = int(valores[4])

            # Ejecutar la simulación de Monte Carlo
            num_simulaciones = 1000
            resultados = simulacion_montecarlo(monto_inicial, tasa_media, plazo, num_simulaciones)

            # Mostrar el histograma de Monte Carlo en la ventana emergente
            mostrar_grafico_monte_carlo(resultados)

        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos seleccionados: {e}")

    
    tk.Button(frame_analisis, text="Simulación de MonteCarlos", 
                command=realizar_analisis_montecarlo).pack(side=tk.LEFT, padx=5)


    def exportar_resultados():
        try:
            financiamientos = obtener_financiamientos_guardados()
            if not financiamientos:
                messagebox.showinfo("Información", "No hay resultados para exportar.")
                return

            nombre_archivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                          filetypes=[("Archivo Excel", "*.xlsx")])
            if not nombre_archivo:
                return  # El usuario canceló el guardado

            escritor = pd.ExcelWriter(nombre_archivo, engine='xlsxwriter')

            for fin in financiamientos:
                tipo = fin['tipo_amortizacion']
                monto = fin['monto']
                tasa = fin['tasa']
                plazo = fin['plazo']
                tir = fin['tir']

                # Calcular el cronograma de pagos según el tipo de amortización
                if tipo == 'alemán':
                    amortizacion = calcular_amortizacion_aleman(monto, tasa, plazo)
                else:
                    amortizacion = calcular_amortizacion_frances(monto, tasa, plazo)

                # Crear DataFrame para el resumen
                resumen = {
                    'ID': [fin['id']],
                    'Tipo': [tipo.capitalize()],
                    'Monto': [monto],
                    'Tasa': [tasa],
                    'Plazo': [plazo],
                    'TIR': [tir]
                }
                df_resumen = pd.DataFrame(resumen)

                # Crear DataFrame para el cronograma de pagos
                df_amortizacion = pd.DataFrame(amortizacion)
                df_amortizacion.index += 1  # Ajustar el índice para que empiece en 1
                df_amortizacion.index.name = 'Periodo'

                # Escribir el resumen y el cronograma en hojas separadas
                df_resumen.to_excel(escritor, sheet_name=f"Fin_{fin['id']}_Resumen", index=False)
                df_amortizacion.to_excel(escritor, sheet_name=f"Fin_{fin['id']}_Cronograma")

            escritor.save()
            messagebox.showinfo("Éxito", f"Resultados exportados correctamente a {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al exportar los resultados: {e}")


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
            tree_financiamientos.column(col, width=100)  # Ajustar ancho de la columna Eliminar

    tree_financiamientos.pack(side=LEFT, fill=tk.BOTH, expand=True)
    
    # Agregar scrollbar al Treeview
    scrollbar = ttk.Scrollbar(frame_list_financiamientos, orient=VERTICAL, command=tree_financiamientos.yview)
    scrollbar.pack(side=LEFT, fill=Y)
    tree_financiamientos.configure(yscrollcommand=scrollbar.set)
    
    # Función para eliminar financiamiento haciendo clic en la columna "Eliminar"
    def on_single_click_main(event):
        region = tree_financiamientos.identify("region", event.x, event.y)
        column = tree_financiamientos.identify_column(event.x)
        if region == "cell" and column == "#7":  # La columna "Eliminar" es la #7
            item = tree_financiamientos.identify_row(event.y)
            if item:
                fin_id = tree_financiamientos.item(item)['values'][0]
                confirmar = messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que deseas eliminar este financiamiento?")
                if confirmar:
                    eliminar_financiamiento(fin_id)
                    messagebox.showinfo("Eliminado", "Financiamiento eliminado correctamente.")
                    cargar_financiamientos()
    
    # Vincular el evento de clic único para eliminar
    tree_financiamientos.bind("<Button-1>", on_single_click_main)
    
    # Función para mostrar el cronograma con doble clic
    def on_double_click_main(event):
        item_id = tree_financiamientos.selection()
        if item_id:
            item = tree_financiamientos.item(item_id)
            financiamiento_id = item['values'][0]
            financiamiento = next((f for f in obtener_financiamientos_guardados() if f['id'] == financiamiento_id), None)
            
            if not financiamiento:
                return
            
            # ...existing code to mostrar_cronograma...
            mostrar_cronograma_financiamiento_main(financiamiento)
    
    # Vincular el evento de doble clic para mostrar el cronograma
    tree_financiamientos.bind("<Double-1>", on_double_click_main)
    
    # ...existing code...
    
    # Eliminar el botón de eliminar seleccionado
    # ...existing code...
    # Por ejemplo, comentar o eliminar las siguientes líneas si existen:
    # def eliminar_financiamiento_seleccionado():
    #     # ...existing code...
    
    # btn_eliminar = tk.Button(frame_botones, text="Eliminar Seleccionado", command=eliminar_financiamiento_seleccionado, bg="#e74c3c", fg="white")
    # btn_eliminar.pack(pady=5, fill=tk.X)
    
    # ...existing code...

    # Función para mostrar el cronograma de un financiamiento en la interfaz principal
    def mostrar_cronograma_financiamiento_main(financiamiento):
        monto = financiamiento['monto']
        tasa = financiamiento['tasa']
        plazo = financiamiento['plazo']
        tipo_amortizacion = financiamiento['tipo_amortizacion']
        portes = financiamiento.get('portes', 0)
        mantenimiento = financiamiento.get('mantenimiento', 0)
        desgravamen = financiamiento.get('desgravamen', 0)
        
        # Calcular el cronograma según el tipo de amortización
        if tipo_amortizacion.lower() == 'alemán':
            cronograma = calcular_amortizacion_aleman(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        elif tipo_amortizacion.lower() == 'frances':
            cronograma = calcular_amortizacion_frances(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        else:
            messagebox.showerror("Error", f"Tipo de amortización desconocido: {tipo_amortizacion}")
            return

        # Mostrar el cronograma en una nueva ventana
        ventana_cronograma = tk.Toplevel()
        ventana_cronograma.title(f"Cronograma de {tipo_amortizacion.capitalize()}")
        ventana_cronograma.geometry("1200x600")  # Ventana más grande

        columns = ("Periodo", "Cuota", "Interés", "Amortización", "Portes", "Mantenimiento", "Desgravamen", "Cuota Total", "Saldo")
        tree_cronograma = ttk.Treeview(ventana_cronograma, columns=columns, show='headings')
        
        # Configurar anchos de columna específicos
        column_widths = {
            "Periodo": 70,
            "Cuota": 100,
            "Interés": 100,
            "Amortización": 100,
            "Portes": 100,
            "Mantenimiento": 100,
            "Desgravamen": 100,
            "Cuota Total": 100,
            "Saldo": 100
        }
        
        for col in columns:
            tree_cronograma.heading(col, text=col)
            tree_cronograma.column(col, anchor="center", width=column_widths[col])

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(ventana_cronograma, orient="vertical", command=tree_cronograma.yview)
        scrollbar.pack(side="right", fill="y")
        tree_cronograma.configure(yscrollcommand=scrollbar.set)
        
        tree_cronograma.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Insertar datos en el Treeview
        for i, fila in enumerate(cronograma, 1):
            tree_cronograma.insert("", "end", values=(
                i,
                f"S/ {fila['cuota']:.2f}",
                f"S/ {fila['interés']:.2f}",
                f"S/ {fila['principal']:.2f}",
                f"S/ {fila['portes']:.2f}",
                f"S/ {fila['mantenimiento']:.2f}",
                f"S/ {fila['desgravamen']:.2f}",
                f"S/ {fila['cuota_total']:.2f}",
                f"S/ {fila['saldo']:.2f}"
            ))

    # ...existing code...

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
    def mostrar_cronograma(event=None):
        global tree_financiamientos
        seleccionado = tree_financiamientos.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un financiamiento para ver el cronograma.")
            return

        item = tree_financiamientos.item(seleccionado)
        financiamiento_id = item['values'][0]  # Asegúrate de usar 'financiamiento_id' correctamente
        financiamiento = next((f for f in obtener_financiamientos_guardados() if f['id'] == financiamiento_id), None)
        
        if not financiamiento:
            return
            
        monto = financiamiento['monto']
        tasa = financiamiento['tasa']
        plazo = financiamiento['plazo']
        tipo_amortizacion = financiamiento['tipo_amortizacion']
        portes = financiamiento.get('portes', 0)
        mantenimiento = financiamiento.get('mantenimiento', 0)
        desgravamen = financiamiento.get('desgravamen', 0)
        
        # Calcular el cronograma según el tipo de amortización
        if tipo_amortizacion.lower() == 'alemán':
            cronograma = calcular_amortizacion_aleman(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        elif tipo_amortizacion.lower() == 'frances':
            cronograma = calcular_amortizacion_frances(monto, tasa, plazo, portes, mantenimiento, desgravamen)
        else:
            messagebox.showerror("Error", f"Tipo de amortización desconocido: {tipo_amortizacion}")
            return

        # Mostrar el cronograma en una nueva ventana
        ventana_cronograma = tk.Toplevel()
        ventana_cronograma.title(f"Cronograma de {tipo_amortizacion.capitalize()}")
        ventana_cronograma.geometry("1200x600")  # Ventana más grande

        columns = ("Periodo", "Cuota", "Interés", "Amortización", "Portes", "Mantenimiento", "Desgravamen", "Cuota Total", "Saldo")
        tree_cronograma = ttk.Treeview(ventana_cronograma, columns=columns, show='headings')
        
        # Configurar anchos de columna específicos
        column_widths = {
            "Periodo": 70,
            "Cuota": 100,
            "Interés": 100,
            "Amortización": 100,
            "Portes": 100,
            "Mantenimiento": 100,
            "Desgravamen": 100,
            "Cuota Total": 100,
            "Saldo": 100
        }
        
        for col in columns:
            tree_cronograma.heading(col, text=col)
            tree_cronograma.column(col, anchor="center", width=column_widths[col])

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(ventana_cronograma, orient="vertical", command=tree_cronograma.yview)
        scrollbar.pack(side="right", fill="y")
        tree_cronograma.configure(yscrollcommand=scrollbar.set)
        
        tree_cronograma.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Insertar datos en el Treeview
        for i, fila in enumerate(cronograma, 1):
            tree_cronograma.insert("", "end", values=(
                i,
                f"S/ {fila['cuota']:.2f}",
                f"S/ {fila['interés']:.2f}",
                f"S/ {fila['principal']:.2f}",
                f"S/ {fila['portes']:.2f}",
                f"S/ {fila['mantenimiento']:.2f}",
                f"S/ {fila['desgravamen']:.2f}",
                f"S/ {fila['cuota_total']:.2f}",
                f"S/ {fila['saldo']:.2f}"
            ))

    # Vincular el evento de selección al Treeview
    tree_financiamientos.bind("<<TreeviewSelect>>", mostrar_cronograma)


    ventana.mainloop()


if __name__=="__main__":
    inicializar_db()
    interfaz_grafica()
