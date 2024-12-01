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
