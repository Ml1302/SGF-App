import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class APIsFinancierasPeru:
    def __init__(self):
        self.base_url_bcrp = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
        self.tickers_peru = {
            'Credicorp': 'BAP',
            'Southern Copper': 'SCCO',
            'Buenaventura': 'BVN',
            'InRetail': 'INRETC1.LM',
            'BBVA Perú': 'BBVAC1.LM'
        }

    def obtener_tasa_referencia_bcrp(self):
        """
        Obtiene la tasa de referencia del BCRP.
        Código de serie: PN00877MM
        """
        fecha_actual = datetime.now()
        # Ajustamos el periodo inicial para asegurarnos de obtener datos
        periodo_inicial = (fecha_actual.replace(year=fecha_actual.year - 2)).strftime('%Y%m')
        periodo_final = fecha_actual.strftime('%Y%m')
        codigo_serie = 'PN00877MM'  # Actualizamos el código de serie
        endpoint = f"{self.base_url_bcrp}/{codigo_serie}/json/{periodo_inicial}/{periodo_final}/esp"
        try:
            print(f"Endpoint Tasa de Referencia: {endpoint}")
            response = requests.get(endpoint)
            if response.status_code != 200:
                print(f"Error en la respuesta: {response.status_code}")
                return None
            data = response.json()
            print(f"Respuesta Tasa de Referencia: {data}")
            if 'periods' in data and data['periods']:
                periods = data['periods']
                # Obtener el último valor disponible
                values = periods[-1].get('values', [])
                if values:
                    valor = values[0]
                    if isinstance(valor, str):
                        return float(valor)
                    elif isinstance(valor, dict) and 'value' in valor:
                        return float(valor['value'])
                print("No hay datos disponibles para Tasa de Referencia")
                return None
            else:
                print("No hay datos en 'periods'")
                return None
        except Exception as e:
            print(f"Error al obtener tasa de referencia: {e}")
            return None

    def obtener_inflacion_anual(self):
        """
        Obtiene la inflación anual (Variación porcentual del IPC a 12 meses).
        Código de serie: PN01283PM
        """
        fecha_actual = datetime.now()
        periodo_inicial = (fecha_actual.replace(year=fecha_actual.year - 2)).strftime('%Y%m')
        periodo_final = fecha_actual.strftime('%Y%m')
        codigo_serie = 'PN01283PM'
        endpoint = f"{self.base_url_bcrp}/{codigo_serie}/json/{periodo_inicial}/{periodo_final}/esp"
        try:
            print(f"Endpoint Inflación Anual: {endpoint}")
            response = requests.get(endpoint)
            if response.status_code != 200:
                print(f"Error en la respuesta: {response.status_code}")
                return None
            data = response.json()
            print(f"Respuesta Inflación Anual: {data}")
            if 'periods' in data and data['periods']:
                periods = data['periods']
                values = periods[-1].get('values', [])
                if values:
                    valor = values[0]
                    if isinstance(valor, str):
                        return float(valor)
                    elif isinstance(valor, dict) and 'value' in valor:
                        return float(valor['value'])
                print("No hay datos disponibles para Inflación")
                return None
            else:
                print("No hay datos en 'periods'")
                return None
        except Exception as e:
            print(f"Error al obtener inflación: {e}")
            return None

    def obtener_datos_acciones_peruanas(self, ticker):
        """
        Obtiene datos históricos de acciones peruanas usando Yahoo Finance
        """
        try:
            stock = yf.Ticker(self.tickers_peru.get(ticker, ticker))
            hist = stock.history(period="1y")
            return hist
        except Exception as e:
            print(f"Error al obtener datos de {ticker}: {e}")
            return None

    def obtener_tipo_cambio(self):
        """
        Obtiene el tipo de cambio USD/PEN (Venta Promedio Interbancario).
        Código de serie: PD04640PD
        """
        fecha_actual = datetime.now()
        # Aseguramos que el periodo inicial cubra un rango con datos disponibles
        periodo_inicial = (fecha_actual - timedelta(days=365)).strftime('%Y%m%d')
        periodo_final = fecha_actual.strftime('%Y%m%d')
        codigo_serie = 'PD04640PD'
        endpoint = f"{self.base_url_bcrp}/{codigo_serie}/json/{periodo_inicial}/{periodo_final}/esp"
        try:
            print(f"Endpoint Tipo de Cambio: {endpoint}")
            response = requests.get(endpoint)
            if response.status_code != 200:
                print(f"Error en la respuesta: {response.status_code}")
                return None
            data = response.json()
            print(f"Respuesta Tipo de Cambio: {data}")
            if 'periods' in data and data['periods']:
                periods = data['periods']
                # Obtener el último valor disponible
                for period in reversed(periods):
                    values = period.get('values', [])
                    if values:
                        valor = values[0]
                        if isinstance(valor, str):
                            return float(valor)
                        elif isinstance(valor, dict) and 'value' in valor:
                            return float(valor['value'])
                print("No hay datos disponibles para Tipo de Cambio")
                return None
            else:
                print("No hay datos en 'periods'")
                return None
        except Exception as e:
            print(f"Error al obtener tipo de cambio: {e}")
            return None