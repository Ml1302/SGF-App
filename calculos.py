def calcular_interes_simple(monto, tasa, plazo):
    return monto * (1 + (tasa / 100) * plazo)

def calcular_interes_compuesto(monto, tasa, plazo):
    return monto * ((1 + tasa / 100) ** plazo)

def calcular_aportaciones_periodicas(monto, tasa, plazo):
    # Fórmula de renta fija: S = P * ((1 + i)^n - 1) / i
    i = tasa / 100
    return monto * (((1 + i) ** plazo - 1) / i)
