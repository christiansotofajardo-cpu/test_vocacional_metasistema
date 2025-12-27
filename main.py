from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

        return render_template(
            "riasec_resultado.html",
            puntajes=puntajes,
            ordenados=ordenados
        )

    return render_template("riasec.html")

# -------------------------
# Autoeficacia
# -------------------------
@app.route("/test/autoeficacia", methods=["GET", "POST"])
def autoeficacia():
    if request.method == "POST":
        total = 0
        for clave, valor in request.form.items():
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

        return render_template(
            "autoeficacia_resultado.html",
            total=total,
            nivel=nivel
        )

    return render_template("autoeficacia.html")

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
