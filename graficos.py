import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def mostrar_grafico(frame_grafico, tipo, monto, tasa, plazo, calcular_interes_compuesto, calcular_interes_simple, calcular_aportaciones_periodicas):
    """
    Genera y muestra el gráfico de proyección de inversión.
    """
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
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def mostrar_grafico_monte_carlo(frame_grafico, resultados):
    """
    Genera y muestra el histograma de resultados de la simulación de Monte Carlo.
    """
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax = figure.add_subplot(111)
    ax.hist(resultados, bins=50, alpha=0.75)
    ax.set_title("Distribución de Resultados de Monte Carlo")
    ax.set_xlabel("Capital Final (S/)")
    ax.set_ylabel("Frecuencia")
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(figure, frame_grafico)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def mostrar_grafico_sensibilidad(frame_grafico, resultados):
    """
    Genera y muestra el gráfico de análisis de sensibilidad.
    """
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
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def graficar_comparativo(escenarios):
    for escenario in escenarios:
        anios = list(range(1, escenario['plazo'] + 1))
        valores = [escenario['funcion'](escenario['monto'], escenario['tasa'], t) for t in anios]
        plt.plot(anios, valores, label=escenario['nombre'])

    plt.title("Comparación de Inversiones")
    plt.xlabel("Años")
    plt.ylabel("Capital (S/)")
    plt.legend()
    plt.grid(True)
    plt.show()

def graficar_comparacion_tir(financiamientos):
    tipos = [f['tipo_amortizacion'].capitalize() for f in financiamientos]
    tirs = [f['tir'] for f in financiamientos]
    
    plt.figure(figsize=(8,6))
    plt.bar(tipos, tirs, color=['blue', 'green', 'orange', 'red', 'purple'][:len(tirs)])
    plt.xlabel('Tipo de Amortización')
    plt.ylabel('TIR (%)')
    plt.title('Comparación de TIR entre Opciones de Financiamiento')
    plt.ylim(0, max(tirs) * 1.2)  # Ajustar el límite superior según el máximo TIR
    for index, value in enumerate(tirs):
        plt.text(index, value + 0.1, f"{value:.2f}%", ha='center')
    plt.show()

# Si decides mantener la funcionalidad de gráficos en otras partes, no realizar cambios.
# Si ya no necesitas gráficos, puedes eliminar este archivo.
