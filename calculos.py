import numpy as np

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
    """Calcula el riesgo del portafolio usando la matriz de correlación"""
    # Implementar cálculo de riesgo usando matriz de correlación
    return sum(p * i['riesgo'] for p, i in zip(pesos, instrumentos))
