import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class APIsFinancierasPeru:
    def __init__(self):
        self.base_url_bcrp = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
        self.tickers_peru = {
            "BVN": "Compañía de Minas Buenaventura",
            "IFS": "Intercorp Financial Services",
            "RIMSEGC1.LM": "RIMAC Seguros",
            "CPAC": "Cementos Pacasmayo S.A.A.",
            "VOLCABC1.LM": "Volcan Compañía Minera S.A.A.",
            'BAP': 'Credicorp' ,
            'SCCO': 'Southern Copper',
            'INRETC1.LM': 'InRetail',
            'BBVAC1.LM': 'BBVA Perú'
        }
    def obtener_datos_acciones_peruanas(self, ticker):
        """
        Obtiene los datos históricos de una acción en Yahoo Finance.
        """
        try:
            accion = yf.Ticker(ticker)
            datos = accion.history(period="1y")  # Datos de un año
            return datos
        except Exception as e:
            print(f"Error al obtener datos de la acción {ticker}: {e}")
            return None
    def obtener_tasa_referencia_bcrp(self):
        """
        Obtiene la tasa de referencia del BCRP.
        Código de serie: PN00877MM
        """
        try:
            codigo_serie = 'PN00877MM'
            fecha_actual = datetime.now()
            periodo_inicial = (fecha_actual.replace(year=fecha_actual.year - 2)).strftime('%Y%m')
            periodo_final = fecha_actual.strftime('%Y%m')
            url = f"{self.base_url_bcrp}/{codigo_serie}/datos?inicio={periodo_inicial}&fin={periodo_final}"
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()
            # Asumiendo que los datos vienen en una lista de registros con 'fecha' y 'valor'
            df = pd.DataFrame(datos)
            tasa_actual = df.iloc[-1]['valor']
            return tasa_actual
        except Exception as e:
            print(f"Error al obtener la tasa de referencia del BCRP: {e}")
            return None

    def obtener_inflacion_anual(self):
        """
        Obtiene la tasa de inflación anual de Perú.
        Código de serie: PN5178A
        """
        try:
            codigo_serie = 'PN5178A'
            fecha_actual = datetime.now()
            periodo_inicial = (fecha_actual.replace(year=fecha_actual.year - 2)).strftime('%Y%m')
            periodo_final = fecha_actual.strftime('%Y%m')
            url = f"{self.base_url_bcrp}/{codigo_serie}/datos?inicio={periodo_inicial}&fin={periodo_final}"
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()
            df = pd.DataFrame(datos)
            inflacion_anual = df.iloc[-1]['valor']
            return inflacion_anual
        except Exception as e:
            print(f"Error al obtener la inflación anual: {e}")
            return None
        
    def obtener_tipo_cambio(self):
        """
        Obtiene el tipo de cambio actual USD a PEN.
        """
        try:
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            tipo_cambio = data['rates']['PEN']
            return tipo_cambio
        except Exception as e:
            print(f"Error al obtener el tipo de cambio: {e}")
            return None