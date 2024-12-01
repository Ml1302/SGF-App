import csv

def exportar_csv(datos, nombre_archivo="inversiones.csv"):
    with open(nombre_archivo, "w", newline="") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(["ID", "Tipo", "Monto", "Tasa (%)", "Plazo (años)", "Resultado"])
        escritor.writerows(datos)
    print(f"Datos exportados a {nombre_archivo}")
