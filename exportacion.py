import csv
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def exportar_datos(datos, nombre_archivo):
    """Exporta los datos a un archivo CSV"""
    df = pd.DataFrame(datos)
    df.to_csv(nombre_archivo, index=False)

def generar_reporte_pdf(datos, nombre_archivo):
    """Genera un reporte PDF con los resultados del análisis"""
    try:
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elementos = []
        styles = getSampleStyleSheet()
    
        # Título
        elementos.append(Paragraph("Reporte de Análisis Financiero", styles['Title']))
        
        # Tabla de resultados
        tabla_data = [[k for k in datos[0].keys()]] + [[str(v) for v in d.values()] for d in datos]
        tabla = Table(tabla_data)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elementos.append(tabla)
        
        doc.build(elementos)
    except Exception as e:
        print(f"Error al generar el reporte PDF: {e}")
