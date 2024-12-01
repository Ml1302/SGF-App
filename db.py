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
