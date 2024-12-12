import sqlite3

def inicializar_db():
    try:
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
                portes REAL DEFAULT 0,
                mantenimiento REAL DEFAULT 0,
                desgravamen REAL DEFAULT 0,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_financiamientos_tipo ON financiamientos (tipo_amortizacion)
        """)

        # Check and add missing columns if necessary
        cursor.execute("PRAGMA table_info(financiamientos)")
        existing_columns = [info[1] for info in cursor.fetchall()]
        required_columns = {
            'portes': 'REAL DEFAULT 0',
            'mantenimiento': 'REAL DEFAULT 0',
            'desgravamen': 'REAL DEFAULT 0'
        }
        for column, definition in required_columns.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE financiamientos ADD COLUMN {column} {definition}")

        conexion.commit()
        conexion.close()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

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

def guardar_financiamiento(tipo_amortizacion, monto, tasa, plazo, tir, portes=0, mantenimiento=0, desgravamen=0):
    """
    Guarda un financiamiento en la base de datos, incluyendo los nuevos campos.
    """
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO financiamientos (tipo_amortizacion, monto, tasa, plazo, tir, portes, mantenimiento, desgravamen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tipo_amortizacion, monto, tasa, plazo, tir, portes, mantenimiento, desgravamen))
    conexion.commit()
    conexion.close()

def obtener_financiamientos_guardados():
    """
    Obtiene los financiamientos guardados, incluyendo los nuevos campos.
    """
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, tipo_amortizacion, monto, tasa, plazo, tir, portes, mantenimiento, desgravamen FROM financiamientos")
    rows = cursor.fetchall()
    conexion.close()

    financiamientos = []
    for row in rows:
        financiamientos.append({
            'id': row[0],
            'tipo_amortizacion': row[1],
            'monto': row[2],
            'tasa': row[3],
            'plazo': row[4],
            'tir': row[5],
            'portes': row[6],
            'mantenimiento': row[7],
            'desgravamen': row[8]
        })
    return financiamientos

def eliminar_financiamiento(financiamiento_id):
    conexion = sqlite3.connect("db.sqlite3")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM financiamientos WHERE id = ?", (financiamiento_id,))
    conexion.commit()
    conexion.close()
