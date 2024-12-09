import sqlite3

def inicializar_db():
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inversiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            monto REAL,
            tasa REAL,
            plazo INTEGER,
            resultado REAL,
            fecha_simulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inversiones_tipo ON inversiones (tipo)
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instrumentos_peru (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            tipo TEXT,
            rendimiento_historico REAL,
            riesgo REAL,
            liquidez TEXT,
            plazo_minimo INTEGER,
            monto_minimo REAL,
            ultima_actualizacion TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financiamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_amortizacion TEXT,
            monto REAL,
            tasa REAL,
            plazo INTEGER,
            tir REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_financiamientos_tipo ON financiamientos (tipo_amortizacion)
    """)
    conexion.commit()
    conexion.close()

def guardar_simulacion(tipo, monto, tasa, plazo, resultado):
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO inversiones (tipo, monto, tasa, plazo, resultado) VALUES (?, ?, ?, ?, ?)",
                   (tipo, monto, tasa, plazo, resultado))
    conexion.commit()
    conexion.close()

def obtener_historial():
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM inversiones")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def guardar_instrumento(nombre, tipo, rendimiento, riesgo, liquidez, plazo_min, monto_min):
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO instrumentos_peru 
        (nombre, tipo, rendimiento_historico, riesgo, liquidez, plazo_minimo, monto_minimo, ultima_actualizacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (nombre, tipo, rendimiento, riesgo, liquidez, plazo_min, monto_min))
    conexion.commit()
    conexion.close()

def guardar_financiamiento(tipo_amortizacion, monto, tasa, plazo, tir):
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO financiamientos (tipo_amortizacion, monto, tasa, plazo, tir)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo_amortizacion, monto, tasa, plazo, tir))  # 'tasa' es la tasa convertida
    conexion.commit()
    conexion.close()

def obtener_financiamientos_guardados():
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, tipo_amortizacion, monto, tasa, plazo, tir FROM financiamientos")
    resultados = cursor.fetchall()
    conexion.close()
    financiamientos = []
    for row in resultados:
        financiamientos.append({
            'id': row[0],
            'tipo_amortizacion': row[1],
            'monto': row[2],
            'tasa': row[3],  # Esta es la tasa convertida
            'plazo': row[4],
            'tir': row[5]
        })
    return financiamientos

def eliminar_financiamiento(financiamiento_id):
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM financiamientos WHERE id = ?", (financiamiento_id,))
    conexion.commit()
    conexion.close()
