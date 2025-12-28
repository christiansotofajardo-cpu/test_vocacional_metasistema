from flask import Flask, render_template, request, redirect, url_for, session, Response
from io import BytesIO
from datetime import datetime
import textwrap
import csv
import os
import psycopg2
from collections import Counter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "metasistema-vocacional"

# =========================
# DB CONNECTION
# =========================
def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluaciones_vocacionales (
                id SERIAL PRIMARY KEY,
                fecha_fin TIMESTAMP,
                nombre TEXT,
                apellido TEXT,
                correo TEXT,
                establecimiento TEXT,
                curso TEXT,
                perfil TEXT,
                autoeficacia_nivel TEXT,
                autoeficacia_total INTEGER,
                r INTEGER,
                i INTEGER,
                a INTEGER,
                s INTEGER,
                e INTEGER,
                c INTEGER
            );
            """)
            conn.commit()

init_db()

# =========================
# HELPERS
# =========================
def safe_get(key, default=""):
    return session.get(key, default) or default

def wrap_lines(text, width=95):
    text = (text or "").strip()
    if not text:
        return ["(sin respuesta)"]
    return textwrap.wrap(text, width=width)

def now():
    return datetime.now()

def require_admin_key():
    admin_key = os.environ.get("ADMIN_KEY", "")
    if not admin_key:
        return True
    return request.args.get("key") == admin_key

# =========================
# ROUTES BÁSICAS
# =========================
@app.get("/")
def home():
    return render_template("index.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        if not request.form.get("consent"):
            return render_template("registro.html", error="Debes aceptar el consentimiento informado.")

        for k in ["nombre", "apellido", "correo", "establecimiento", "curso"]:
            session[k] = request.form.get(k, "").strip()

        session["inicio"] = now()
        return redirect("/test/riasec")

    return render_template("registro.html")

# =========================
# RIASEC
# =========================
@app.route("/test/riasec", methods=["GET", "POST"])
def riasec():
    if request.method == "POST":
        puntajes = {k: 0 for k in "RIASEC"}
        for k, v in request.form.items():
            if k[0] in puntajes:
                puntajes[k[0]] += int(v)

        orden = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
        session["perfil"] = f"{orden[0][0]}–{orden[1][0]}"
        session["puntajes"] = puntajes

        return redirect("/test/autoeficacia")

    return render_template("riasec.html")

# =========================
# AUTOEFICACIA
# =========================
@app.route("/test/autoeficacia", methods=["GET", "POST"])
def autoeficacia():
    if request.method == "POST":
        total = sum(int(v) for v in request.form.values())
        nivel = "Baja" if total <= 30 else "Media" if total <= 45 else "Alta"
        session["auto_total"] = total
        session["auto_nivel"] = nivel
        return redirect("/resultado")

    return render_template("autoeficacia.html")

# =========================
# RESULTADO
# =========================
@app.get("/resultado")
def resultado():
    return render_template(
        "interpretacion.html",
        perfil=session.get("perfil"),
        nivel=session.get("auto_nivel"),
        texto="Orientación vocacional formativa."
    )

# =========================
# METASISTEMA Y GUARDADO DB
# =========================
@app.route("/metasistema", methods=["GET", "POST"])
def metasistema():
    if request.method == "POST":
        with get_db() as conn:
            with conn.cursor() as cur:
                p = session["puntajes"]
                cur.execute("""
                INSERT INTO evaluaciones_vocacionales
                (fecha_fin, nombre, apellido, correo, establecimiento, curso,
                 perfil, autoeficacia_nivel, autoeficacia_total,
                 r, i, a, s, e, c)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    now(),
                    session.get("nombre"),
                    session.get("apellido"),
                    session.get("correo"),
                    session.get("establecimiento"),
                    session.get("curso"),
                    session.get("perfil"),
                    session.get("auto_nivel"),
                    session.get("auto_total"),
                    p["R"], p["I"], p["A"], p["S"], p["E"], p["C"]
                ))
                conn.commit()

        return redirect("/cierre")

    return render_template("metasistema.html")

# =========================
# CIERRE
# =========================
@app.get("/cierre")
def cierre():
    return render_template("cierre.html",
        perfil=session.get("perfil"),
        nivel=session.get("auto_nivel")
    )

# =========================
# PANEL ADMIN (DB REAL)
# =========================
@app.get("/admin")
def admin():
    if not require_admin_key():
        return Response("No autorizado", 401)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evaluaciones_vocacionales ORDER BY fecha_fin DESC")
            rows = cur.fetchall()

    return render_template("admin.html", rows=rows, total=len(rows))

# =========================
# EXPORT CSV
# =========================
@app.get("/admin.csv")
def admin_csv():
    if not require_admin_key():
        return Response("No autorizado", 401)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evaluaciones_vocacionales ORDER BY fecha_fin DESC")
            rows = cur.fetchall()

    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow([
        "id","fecha","nombre","apellido","correo","establecimiento","curso",
        "perfil","auto_nivel","auto_total","R","I","A","S","E","C"
    ])
    for r in rows:
        writer.writerow(r)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=vocacional.csv"}
    )

if __name__ == "__main__":
    app.run()

