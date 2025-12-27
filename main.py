from flask import Flask, render_template, request, redirect, url_for, session, Response
from io import BytesIO
from datetime import datetime
import textwrap

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "metasistema-vocacional"

# -------------------------
# Helpers
# -------------------------
def safe_get(key, default=""):
    v = session.get(key, default)
    return v if v is not None else default

def wrap_lines(text, width=95):
    text = (text or "").strip()
    if not text:
        return ["(sin respuesta)"]
    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=width))
    return lines

# -------------------------
# Home
# -------------------------
@app.get("/")
def home():
    return render_template("index.html")

# -------------------------
# Registro
# -------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip()
        establecimiento = request.form.get("establecimiento", "").strip()
        curso = request.form.get("curso", "").strip()
        consent = request.form.get("consent")

        if not consent:
            return render_template(
                "registro.html",
                error="Debes aceptar el consentimiento informado para continuar."
            )

        # Guardar en sesión (para informe)
        session["nombre"] = nombre
        session["apellido"] = apellido
        session["correo"] = correo
        session["establecimiento"] = establecimiento
        session["curso"] = curso
        session["timestamp_inicio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return redirect(url_for("riasec"))

    return render_template("registro.html")

# -------------------------
# RIASEC
# -------------------------
@app.route("/test/riasec", methods=["GET", "POST"])
def riasec():
    if request.method == "POST":
        respuestas = request.form
        puntajes = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

        for clave, valor in respuestas.items():
            letra = clave[0]
            if letra in puntajes:
                try:
                    puntajes[letra] += int(valor)
                except ValueError:
                    pass

        ordenados = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)

        session["riasec_puntajes"] = puntajes
        session["riasec_top"] = [ordenados[0][0], ordenados[1][0]]
        session["perfil"] = f"{ordenados[0][0]}–{ordenados[1][0]}"

        return redirect(url_for("autoeficacia"))

    return render_template("riasec.html")

# -------------------------
# Autoeficacia
# -------------------------
@app.route("/test/autoeficacia", methods=["GET", "POST"])
def autoeficacia():
    if request.method == "POST":
        total = 0
        for valor in request.form.values():
            try:
                total += int(valor)
            except ValueError:
                pass

        if total <= 30:
            nivel = "Baja"
        elif total <= 45:
            nivel = "Media"
        else:
            nivel = "Alta"

        session["autoeficacia_total"] = total
        session["autoeficacia_nivel"] = nivel

        return redirect(url_for("interpretacion"))

    return render_template("autoeficacia.html")

# -------------------------
# Interpretación Integrada
# -------------------------
@app.get("/resultado")
def interpretacion():
    top = session.get("riasec_top", [])
    nivel = session.get("autoeficacia_nivel", "No disponible")

    if len(top) < 2:
        return redirect(url_for("home"))

    perfil = safe_get("perfil", f"{top[0]}–{top[1]}")

    interpretaciones = {
        "Alta": "Presentas una percepción sólida de tu capacidad para enfrentar desafíos y llevar a cabo tus intereses.",
        "Media": "Percibes capacidades adecuadas, aunque puedes beneficiarte de apoyo y experiencias de fortalecimiento.",
        "Baja": "Podrías requerir mayor acompañamiento para desarrollar confianza en tus capacidades."
    }

    return render_template(
        "interpretacion.html",
        perfil=perfil,
        nivel=nivel,
        texto=interpretaciones.get(nivel, "")
    )

# -------------------------
# MetaSistema – Consignas abiertas
# -------------------------
@app.route("/metasistema", methods=["GET", "POST"])
def metasistema():
    if request.method == "POST":
        session["meta_q1"] = request.form.get("q1", "").strip()
        session["meta_q2"] = request.form.get("q2", "").strip()
        session["meta_q3"] = request.form.get("q3", "").strip()
        session["timestamp_fin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return redirect(url_for("cierre"))

    return render_template("metasistema.html")

# -------------------------
# Cierre
# -------------------------
@app.get("/cierre")
def cierre():
    return render_template(
        "cierre.html",
        perfil=safe_get("perfil", "No disponible"),
        nivel=safe_get("autoeficacia_nivel", "No disponible")
    )

# -------------------------
# Informe HTML
# -------------------------
@app.get("/informe")
def informe():
    data = {
        "nombre": safe_get("nombre", ""),
        "apellido": safe_get("apellido", ""),
        "correo": safe_get("correo", ""),
        "establecimiento": safe_get("establecimiento", ""),
        "curso": safe_get("curso", ""),
        "inicio": safe_get("timestamp_inicio", ""),
        "fin": safe_get("timestamp_fin", ""),
        "perfil": safe_get("perfil", "No disponible"),
        "auto_nivel": safe_get("autoeficacia_nivel", "No disponible"),
        "auto_total": safe_get("autoeficacia_total", ""),
        "puntajes": session.get("riasec_puntajes", {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}),
        "q1": safe_get("meta_q1", ""),
        "q2": safe_get("meta_q2", ""),
        "q3": safe_get("meta_q3", ""),
    }
    return render_template("informe.html", **data)

# -------------------------
# Informe PDF (descarga)
# -------------------------
@app.get("/informe.pdf")
def informe_pdf():
    nombre = safe_get("nombre", "").strip()
    apellido = safe_get("apellido", "").strip()
    perfil = safe_get("perfil", "No disponible")
    auto_nivel = safe_get("autoeficacia_nivel", "No disponible")
    auto_total = safe_get("autoeficacia_total", "—")
    establecimiento = safe_get("establecimiento", "—")
    curso = safe_get("curso", "—")
    inicio = safe_get("timestamp_inicio", "—")
    fin = safe_get("timestamp_fin", "—")
    puntajes = session.get("riasec_puntajes", {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0})

    q1 = safe_get("meta_q1", "")
    q2 = safe_get("meta_q2", "")
    q3 = safe_get("meta_q3", "")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Informe Vocacional MetaSistema (v1.0)")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Fecha generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 18

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Identificación")
    y -= 14

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Nombre: {nombre} {apellido}".strip() or "—")
    y -= 12
    c.drawString(50, y, f"Establecimiento: {establecimiento}")
    y -= 12
    c.drawString(50, y, f"Curso / Nivel: {curso}")
    y -= 12
    c.drawString(50, y, f"Inicio: {inicio}   |   Término: {fin}")
    y -= 18

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Resultados cuantitativos")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Perfil RIASEC predominante: {perfil}")
    y -= 12
    c.drawString(50, y, f"Autoeficacia: {auto_nivel} (puntaje total: {auto_total})")
    y -= 12

    c.drawString(50, y, "Puntajes por dimensión (10–40):")
    y -= 12
    c.drawString(70, y, f"R: {puntajes.get('R', 0)}   I: {puntajes.get('I', 0)}   A: {puntajes.get('A', 0)}")
    y -= 12
    c.drawString(70, y, f"S: {puntajes.get('S', 0)}   E: {puntajes.get('E', 0)}   C: {puntajes.get('C', 0)}")
    y -= 18

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Módulo MetaSistema (reflexión)")
    y -= 14
    c.setFont("Helvetica", 10)

    def section(title, text):
        nonlocal y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, title)
        y -= 12
        c.setFont("Helvetica", 10)
        for line in wrap_lines(text, width=95):
            if y < 70:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(50, y, line)
            y -= 12
        y -= 8

    section("1) Motivación personal:", q1)
    section("2) Habilidades importantes:", q2)
    section("3) Proyección futura:", q3)

    if y < 110:
        c.showPage()
        y = height - 50

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Nota ética")
    y -= 14
    c.setFont("Helvetica", 10)
    for line in wrap_lines(
        "Este informe entrega una orientación formativa basada en intereses (RIASEC), autoeficacia y reflexión personal. "
        "No constituye un diagnóstico ni una recomendación cerrada de carrera; su propósito es apoyar la conversación vocacional "
        "y la toma de decisiones informada.",
        width=95
    ):
        c.drawString(50, y, line)
        y -= 12

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()

    filename = "informe_vocacional_metasistema.pdf"
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

