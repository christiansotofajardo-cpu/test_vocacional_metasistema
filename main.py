from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "metasistema-vocacional"

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
        consent = request.form.get("consent")
        if not consent:
            return render_template(
                "registro.html",
                error="Debes aceptar el consentimiento informado para continuar."
            )
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

    perfil = f"{top[0]}–{top[1]}"

    interpretaciones = {
        "Alta": "Presentas una percepción sólida de tu capacidad para enfrentar desafíos y llevar a cabo tus intereses.",
        "Media": "Percibes capacidades adecuadas, aunque puedes beneficiarte de apoyo y experiencias de fortalecimiento.",
        "Baja": "Podrías requerir mayor acompañamiento para desarrollar confianza en tus capacidades."
    }

    session["perfil"] = perfil

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
        session["meta_q1"] = request.form.get("q1")
        session["meta_q2"] = request.form.get("q2")
        session["meta_q3"] = request.form.get("q3")

        return redirect(url_for("cierre"))

    return render_template("metasistema.html")

# -------------------------
# Cierre
# -------------------------
@app.get("/cierre")
def cierre():
    return render_template(
        "cierre.html",
        perfil=session.get("perfil", "No disponible"),
        nivel=session.get("autoeficacia_nivel", "No disponible")
    )

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

