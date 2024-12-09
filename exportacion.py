import csv
from datetime import datetime
from fpdf import FPDF

def exportar_datos(datos, nombre_archivo):
    """
    Exporta los datos a un archivo CSV.
    
    Parámetros:
    - datos: Lista de diccionarios con los datos a exportar.
    - nombre_archivo: Nombre del archivo CSV.
    """
    keys = datos[0].keys() if datos else []
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
        dict_writer = csv.DictWriter(archivo, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(datos)

def generar_reporte_pdf(datos, nombre_archivo):
    """
    Genera un reporte en PDF con los datos proporcionados.
    
    Parámetros:
    - datos: Lista de diccionarios con los datos del reporte.
    - nombre_archivo: Nombre del archivo PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.cell(200, 10, txt="Reporte de Finanzas", ln=True, align='C')
    
    # Tabla de Datos
    for registro in datos:
        linea = ""
        for valor in registro.values():
            linea += f"{valor}\t"
        pdf.multi_cell(0, 10, linea)
        pdf.ln(2)
    
    pdf.output(nombre_archivo)
