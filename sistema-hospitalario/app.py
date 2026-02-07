from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "razohospital123"

# ====== CONFIGURA TU CORREO AQUÍ ======
CORREO_REMITENTE = "tucorreo@gmail.com"
CLAVE_APLICACION = "CLAVE_DE_APLICACION"
# ====================================

def get_db():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn

def enviar_correo(destino, asunto, mensaje):
    msg = MIMEText(mensaje, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = CORREO_REMITENTE
    msg["To"] = destino

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(CORREO_REMITENTE, CLAVE_APLICACION)
    server.send_message(msg)
    server.quit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        pwd = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (user, pwd))
        data = cur.fetchone()

        if data:
            session["usuario"] = data["usuario"]
            session["rol"] = data["rol"]
            return redirect("/dashboard")
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        usuario = request.form["usuario"]
        password = request.form["password"]

        if len(password) < 8:
            flash("La contraseña debe tener mínimo 8 caracteres")
            return redirect("/registro")

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                (nombre, usuario, password, "usuario")
            )
            db.commit()
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Ese usuario ya existe")

    return render_template("registro.html")


@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if session["rol"] == "admin":
        cur.execute("SELECT * FROM citas")
    else:
        cur.execute("SELECT * FROM citas WHERE usuario=?", (session["usuario"],))

    citas = cur.fetchall()
    return render_template("dashboard.html", citas=citas)


@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    if "usuario" not in session:
        return redirect("/")

    if request.method == "POST":
        paciente = request.form["paciente"]
        correo = request.form["correo"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        usuario = session["usuario"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO citas (paciente, correo, fecha, hora, usuario, estado) VALUES (?, ?, ?, ?, ?, ?)",
            (paciente, correo, fecha, hora, usuario, "pendiente")
        )
        db.commit()
        flash("Cita enviada. Queda en estado PENDIENTE.")

    return render_template("reservas.html")


@app.route("/estado/<int:id>/<accion>")
def cambiar_estado(id, accion):
    if "usuario" not in session or session["rol"] != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM citas WHERE id=?", (id,))
    cita = cur.fetchone()

    if cita:
        if accion == "aprobar":
            nuevo_estado = "aprobada"
            mensaje = f"""Hola {cita['paciente']},

Tu cita para el {cita['fecha']} a las {cita['hora']} ha sido APROBADA.

Gracias por usar el Sistema de Gestión Hospitalaria.
"""
        else:
            nuevo_estado = "rechazada"
            mensaje = f"""Hola {cita['paciente']},

Tu cita para el {cita['fecha']} a las {cita['hora']} ha sido RECHAZADA.

Por favor intenta con otro horario.
"""

        cur.execute("UPDATE citas SET estado=? WHERE id=?", (nuevo_estado, id))
        db.commit()

        try:
            enviar_correo(cita["correo"], "Estado de tu cita médica", mensaje)
        except:
            pass

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
