import matplotlib.pyplot as plt

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
