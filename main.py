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
        logo = Image.open("assets\logo.png")
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

    notebook.add(tab_inversiones, text="Opciones de financiamiento")
    notebook.add(tab_financiamientos, text="Financiamientos guardados")
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

    # Declarar variables para opciones de financiamiento
    tipo_var = tk.StringVar(value="alemán")
    entrada_fin_monto = tk.Entry(frame_datos)
    entrada_fin_tasa = tk.Entry(frame_datos)
    entrada_fin_plazo = tk.Entry(frame_datos)
    
    # Variables para unidades
    unidad_tasa = tk.StringVar(value="Anual")
    unidad_plazo = tk.StringVar(value="Meses")
    
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

    # Agregar botón para agregar financiamiento
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
