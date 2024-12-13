import numpy as np
import numpy_financial as npf
from scipy import stats

def calcular_interes_simple(monto, tasa, plazo):
    return monto * (1 + (tasa / 100) * plazo)

def calcular_interes_compuesto(monto, tasa, plazo):
    return monto * ((1 + tasa / 100) ** plazo)

def calcular_aportaciones_periodicas(monto, tasa, plazo):
    # Fórmula de renta fija: S = P * ((1 + i)^n - 1) / i
    i = tasa / 100
    return monto * (((1 + i) ** plazo - 1) / i)

def calcular_var_historico(retornos, nivel_confianza=0.95):
    """Calcula el Valor en Riesgo (VaR) histórico"""
    return np.percentile(retornos, (1 - nivel_confianza) * 100)

def ajustar_por_inflacion(monto, tasa_inflacion, plazo):
    """Ajusta el valor futuro considerando la inflación"""
    return monto / ((1 + tasa_inflacion/100) ** plazo)

def calcular_ratio_sharpe(retorno_esperado, tasa_libre_riesgo, volatilidad):
    """Calcula el ratio de Sharpe"""
    return (retorno_esperado - tasa_libre_riesgo) / volatilidad

def analizar_portafolio(montos, instrumentos):
    """Analiza un portafolio diversificado"""
    total = sum(montos)
    pesos = [m/total for m in montos]
    retorno_esperado = sum(p * i['retorno'] for p, i in zip(pesos, instrumentos))
    riesgo = calcular_riesgo_portafolio(pesos, instrumentos)
    return retorno_esperado, riesgo

def calcular_riesgo_portafolio(pesos, instrumentos):
    """Calcula el riesgo del portafolio usando una matriz de correlación simplificada"""
    # Ejemplo simplificado asumiendo correlación 0
    riesgo = 0
    for peso, instrumento in zip(pesos, instrumentos):
        riesgo += (peso ** 2) * (instrumento['riesgo'] ** 2)
    return np.sqrt(riesgo)

def calcular_amortizacion_aleman(monto, tasa, plazo, portes=0, mantenimiento=0, desgravamen=0):
    """
    Calcula la tabla de amortización alemana incluyendo portes, mantenimiento y desgravamen.
    """
    tasa_decimal = tasa / 100
    amortizacion_constante = monto / plazo
    amortizaciones = []
    saldo = monto
    for _ in range(plazo):
        interes = saldo * tasa_decimal
        cuota = amortizacion_constante + interes
        cuota_total = cuota + portes + mantenimiento + desgravamen
        saldo -= amortizacion_constante
        amortizaciones.append({
            'cuota': cuota,
            'interés': interes,
            'principal': amortizacion_constante,
            'portes': portes,
            'mantenimiento': mantenimiento,
            'desgravamen': desgravamen,
            'cuota_total': cuota_total,
            'saldo': max(0, saldo)  # Evitar saldos negativos
        })
    return amortizaciones

def calcular_amortizacion_frances(monto, tasa, plazo, portes=0, mantenimiento=0, desgravamen=0):
    """
    Calcula la tabla de amortización francesa incluyendo portes, mantenimiento y desgravamen.
    """
    tasa_decimal = tasa / 100
    cuota = npf.pmt(tasa_decimal, plazo, -monto)
    amortizaciones = []
    saldo = monto
    for _ in range(plazo):
        interes = saldo * tasa_decimal
        principal = cuota - interes
        saldo -= principal
        cuota_total = cuota + portes + mantenimiento + desgravamen
        amortizaciones.append({
            'cuota': cuota,
            'interés': interes,
            'principal': principal,
            'portes': portes,
            'mantenimiento': mantenimiento,
            'desgravamen': desgravamen,
            'cuota_total': cuota_total,
            'saldo': max(0, saldo)  # Evitar saldos negativos
        })
    return amortizaciones

def convertir_tasa(tasa_original, periodo_origen, periodo_destino):
    """
    Convierte una tasa de interés de un periodo a otro.

    Parámetros:
    - tasa_original: Tasa de interés en formato decimal (por ejemplo, 0.12 para 12%).
    - periodo_origen: Número de periodos por año de la tasa original.
    - periodo_destino: Número de periodos por año de la tasa deseada.

    Retorna:
    - Tasa convertida en formato decimal.
    """
    tasa_convertida = (1 + tasa_original) ** (periodo_destino / periodo_origen) - 1
    return tasa_convertida

def calcular_tir(flujos):
    """
    Calcula la TIR usando los flujos de caja.

    Parámetros:
    - flujos: Lista donde el primer valor es el préstamo (negativo) y los demás son los pagos positivos

    Retorna:
    - TIR como porcentaje, basado únicamente en el número de períodos
    """
    try:
        # Validar que los flujos tengan un cambio de signo
        if len(flujos) < 2 or all(f > 0 for f in flujos) or all(f < 0 for f in flujos):
            print("Los flujos de caja no tienen cambio de signo necesario para calcular la TIR.")
            return 0  # Condición de cálculo no válida
        
        # Calcular la TIR directamente
        tir = npf.irr(flujos)
        
        # Validar si el valor es finito
        if np.isfinite(tir):
            return tir * 100  # Retornar como porcentaje
        else:
            return 0
    except Exception as e:
        print(f"Error al calcular la TIR: {e}")
        return 0


def calcular_van(flujos, tasa_descuento):
    if not isinstance(flujos, (list, tuple)):
        raise TypeError(f"Se esperaba una lista o tupla de flujos, pero se recibió: {type(flujos)}")
    return sum(flujo / ((1 + tasa_descuento) ** i) for i, flujo in enumerate(flujos))

def analisis_sensibilidad(monto, tasa_base, plazo, rango_tasa=2, pasos=5):
    """Realiza análisis de sensibilidad variando la tasa de interés"""
    resultados = []
    tasas = np.linspace(tasa_base - rango_tasa, tasa_base + rango_tasa, pasos)
    for tasa in tasas:
        van = calcular_van([-monto] + [monto * tasa/100] * plazo, tasa)
        resultados.append({'tasa': tasa, 'van': van})
    return resultados

def calcular_payback(flujos):
    """Calcula el período de recuperación de la inversión"""
    flujo_acumulado = 0
    for i, flujo in enumerate(flujos[1:], 1):
        flujo_acumulado += flujo
        if flujo_acumulado >= abs(flujos[0]):
            return i
    return None

def calcular_indicadores_riesgo(flujos_historicos):
    """Calcula indicadores de riesgo basados en datos históricos"""
    retornos = np.diff(flujos_historicos) / flujos_historicos[:-1]
    return {
        'volatilidad': np.std(retornos) * np.sqrt(12),  # Anualizada
        'var_95': stats.norm.ppf(0.95, np.mean(retornos), np.std(retornos))
    }

def comparar_alternativas_financiamiento(opciones, perfil_riesgo='moderado'):
    """Compara diferentes alternativas de financiamiento según el perfil de riesgo"""
    resultados = []
    pesos = {'tir': 0.4, 'plazo': 0.3, 'cuota': 0.3}
    
    if (perfil_riesgo == 'conservador'):
        pesos = {'tir': 0.3, 'plazo': 0.4, 'cuota': 0.3}
    elif (perfil_riesgo == 'agresivo'):
        pesos = {'tir': 0.5, 'plazo': 0.2, 'cuota': 0.3}
    
    for opcion in opciones:
        score = (opcion['tir'] * pesos['tir'] + 
                (1/opcion['plazo']) * pesos['plazo'] + 
                (1/opcion['cuota']) * pesos['cuota'])
        resultados.append({'opcion': opcion, 'score': score})
    
    return sorted(resultados, key=lambda x: x['score'], reverse=True)

def analizar_riesgo_inversion(flujos_historicos, flujos_futuros, tasa_descuento):
    """
    Analiza el riesgo de una inversión utilizando métricas financieras como el VAN y otros indicadores de riesgo.

    :param flujos_historicos: Flujos históricos para calcular indicadores de riesgo.
    :param flujos_futuros: Flujos futuros proyectados para calcular el VAN.
    :param tasa_descuento: Tasa de descuento para el análisis.
    :return: Diccionario con los resultados del análisis de riesgo.
    """
    # Calcular indicadores de riesgo
    indicadores_riesgo = calcular_indicadores_riesgo(flujos_historicos)

    # Calcular VAN
    van = calcular_van(tasa_descuento, flujos_futuros)

    return {
        "volatilidad": indicadores_riesgo["volatilidad"],
        "var_95": indicadores_riesgo["var_95"],
        "van": van
    }

def simulacion_montecarlo(monto_inicial, tasa_media, plazo, num_simulaciones=1000, desviacion_estandar=0.02):
    """
    Simula el capital final utilizando Monte Carlo para un conjunto de tasas de interés aleatorias.
    
    Parámetros:
    - monto_inicial: El monto inicial de la inversión.
    - tasa_media: Tasa de interés promedio (en formato decimal, por ejemplo, 0.05 para 5%).
    - plazo: El número de periodos (años, meses, etc.).
    - num_simulaciones: Número de simulaciones a ejecutar.
    - desviacion_estandar: Desviación estándar de la tasa de interés, para simular variabilidad.
    
    Retorna:
    - Una lista de los resultados de capital final para cada simulación.
    """
    resultados = []
    for _ in range(num_simulaciones):
        # Generar una tasa de interés aleatoria basada en una distribución normal
        tasa_simulada = np.random.normal(tasa_media, desviacion_estandar)
        
        # Asegurarse de que la tasa no sea negativa
        if tasa_simulada < 0:
            tasa_simulada = 0
        
        # Calcular el capital final usando interés compuesto
        capital_final = monto_inicial * (1 + tasa_simulada) ** plazo
        resultados.append(capital_final)
    
    return resultados
def simulacion_monte_carlo2(tasa_interes, capital_inicial, dias_simulacion, num_simulaciones):
    """
    Simula el rendimiento del capital usando Monte Carlo.
    """
    resultados = []
    
    for _ in range(num_simulaciones):
        rendimiento_dia = np.random.normal(tasa_interes / 252, 0.02, dias_simulacion)
        capital_final = capital_inicial * np.exp(np.cumsum(rendimiento_dia)[-1])
        resultados.append(capital_final)
    
    return resultados

def analisis_riesgo_simulacion(resultados):
    """
    Analiza el riesgo basado en los resultados de la simulación de Monte Carlo.
    """
    return {
        "capital_final_promedio": np.mean(resultados),
        "capital_final_maximo": np.max(resultados),
        "capital_final_minimo": np.min(resultados),
        "desviacion_estandar": np.std(resultados)
    }
