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
        return redirect(url_for(
            "riasec",
            nombre=request.form.get("nombre"),
            apellido=request.form.get("apellido"),
            establecimiento=request.form.get("establecimiento"),
            curso=request.form.get("curso")
        ))
    return render_template("registro.html")


# --------------------------------------------------
# RIASEC
# --------------------------------------------------
@app.route("/riasec", methods=["GET", "POST"])
def riasec():
    if request.method == "POST":
        return redirect(url_for(
            "riasec_resultado",
            nombre=request.form.get("nombre"),
            apellido=request.form.get("apellido"),
            establecimiento=request.form.get("establecimiento"),
            curso=request.form.get("curso")
        ))

    return render_template(
        "riasec.html",
        nombre=request.args.get("nombre"),
        apellido=request.args.get("apellido"),
        establecimiento=request.args.get("establecimiento"),
        curso=request.args.get("curso")
    )


@app.route("/riasec_resultado", methods=["GET", "POST"])
def riasec_resultado():
    perfil_riasec = "Realista – Investigativo"

    return render_template(
        "riasec_resultado.html",
        perfil_riasec=perfil_riasec,
        **request.args
    )


# --------------------------------------------------
# AUTOEFICACIA
# --------------------------------------------------
@app.route("/autoefficacia", methods=["GET", "POST"])
def autoefficacia():
    if request.method == "POST":
        return redirect(url_for(
            "autoefficacia_resultado",
            **request.form
        ))

    return render_template("autoefficacia.html", **request.args)


@app.route("/autoefficacia_resultado", methods=["GET", "POST"])
def autoefficacia_resultado():
    autoeficacia = 27

    return render_template(
        "autoefficacia_resultado.html",
        autoeficacia=autoeficacia,
        **request.args
    )


# --------------------------------------------------
# METASISTEMA
# --------------------------------------------------
@app.route("/metasistema", methods=["GET", "POST"])
def metasistema():
    if request.method == "POST":
        return redirect(url_for(
            "interpretacion",
            **request.form
        ))

    return render_template("metasistema.html", **request.args)


# --------------------------------------------------
# INTERPRETACION
# --------------------------------------------------
@app.route("/interpretacion", methods=["GET", "POST"])
def interpretacion():
    if request.method == "POST":
        return redirect(url_for(
            "informe",
            **request.form
        ))

    return render_template("interpretacion.html", **request.args)


# --------------------------------------------------
# INFORME FINAL (v1.1 AUTOMÁTICO)
# --------------------------------------------------
@app.route("/informe")
def informe():
    fecha = datetime.now().strftime("%d-%m-%Y %H:%M")

    nombre = request.args.get("nombre")
    apellido = request.args.get("apellido")
    establecimiento = request.args.get("establecimiento")
    curso = request.args.get("curso")

    perfil_riasec = "Realista – Investigativo"
    autoeficacia = 27
    nivel_autoeficacia = "Bajo–Medio"

    motivacion = request.args.get("motivacion", "Creación")
    habilidad = request.args.get("habilidad", "Sociabilidad")
    proyeccion = request.args.get("proyeccion", "Desarrollo de aplicaciones")

    # Guardar en DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO evaluaciones
        (fecha, nombre, apellido, establecimiento, curso,
         riasec, autoeficacia, motivacion, habilidad, proyeccion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fecha, nombre, apellido, establecimiento, curso,
        perfil_riasec, autoeficacia, motivacion, habilidad, proyeccion
    ))
    conn.commit()
    conn.close()

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
# CIERRE
# --------------------------------------------------
@app.route("/cierre")
def cierre():
    return render_template("cierre.html")


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
