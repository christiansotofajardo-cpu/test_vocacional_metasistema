from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_PATH = "vocacional.db"


# --------------------------------------------------
# DB INIT
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre TEXT,
            apellido TEXT,
            establecimiento TEXT,
            curso TEXT,
            riasec TEXT,
            autoeficacia INTEGER,
            motivacion TEXT,
            habilidad TEXT,
            proyeccion TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# REGISTRO
# --------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "establecimiento": request.form.get("establecimiento"),
            "curso": request.form.get("curso"),
        }
        return redirect(url_for("test", **data))
    return render_template("registro.html")


# --------------------------------------------------
# TEST (SIMULACIÓN CONTROLADA)
# --------------------------------------------------
@app.route("/test")
def test():
    return render_template(
        "test.html",
        nombre=request.args.get("nombre"),
        apellido=request.args.get("apellido"),
        establecimiento=request.args.get("establecimiento"),
        curso=request.args.get("curso")
    )


# --------------------------------------------------
# RESULTADO + INFORME
# --------------------------------------------------
@app.route("/resultado", methods=["POST"])
def resultado():
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    establecimiento = request.form.get("establecimiento")
    curso = request.form.get("curso")

    # --- Resultados simulados (v1.0 defendible)
    perfil_riasec = "Realista – Investigativo"
    autoeficacia = 27
    nivel_autoeficacia = "Bajo–Medio"

    # --- MetaSistema (abierto)
    motivacion = request.form.get("motivacion", "Creación")
    habilidad = request.form.get("habilidad", "Sociabilidad")
    proyeccion = request.form.get("proyeccion", "Desarrollo de aplicaciones")

    fecha = datetime.now().strftime("%d-%m-%Y %H:%M")

    # --- Guardar en DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO evaluaciones
        (fecha, nombre, apellido, establecimiento, curso, riasec,
         autoeficacia, motivacion, habilidad, proyeccion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fecha, nombre, apellido, establecimiento, curso,
        perfil_riasec, autoeficacia, motivacion, habilidad, proyeccion
    ))
    conn.commit()
    conn.close()

    # --- Render informe automático v1.1
    return render_template(
        "informe.html",
        fecha=fecha,
        nombre=nombre,
        apellido=apellido,
        establecimiento=establecimiento,
        curso=curso,
        perfil_riasec=perfil_riasec,
        autoeficacia=autoeficacia,
        nivel_autoeficacia=nivel_autoeficacia,
        motivacion=motivacion,
        habilidad=habilidad,
        proyeccion=proyeccion
    )


# --------------------------------------------------
# ADMIN
# --------------------------------------------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT fecha, nombre, apellido, establecimiento, curso, riasec, autoeficacia
        FROM evaluaciones
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    conn.close()

    return render_template("admin.html", rows=rows)


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


