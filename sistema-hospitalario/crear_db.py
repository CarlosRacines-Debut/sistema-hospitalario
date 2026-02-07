import sqlite3

db = sqlite3.connect("hospital.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    usuario TEXT UNIQUE,
    password TEXT,
    rol TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente TEXT,
    correo TEXT,
    fecha TEXT,
    hora TEXT,
    usuario TEXT,
    estado TEXT
)
""")

cur.execute("""
INSERT OR IGNORE INTO usuarios (nombre, usuario, password, rol)
VALUES ('Carlos Racines', 'admin', '12345678', 'admin')
""")

db.commit()
db.close()

print("Base de datos lista ✅")
