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
            resultado REAL
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
