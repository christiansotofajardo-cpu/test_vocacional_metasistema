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

        # Inicializar puntajes
        puntajes = {
            "R": 0,
            "I": 0,
            "A": 0,
            "S": 0,
            "E": 0,
            "C": 0
        }

        # Sumar respuestas por letra
        for clave, valor in respuestas.items():
            letra = clave[0]  # R1 -> R
            if letra in puntajes:
                try:
                    puntajes[letra] += int(valor)
                except ValueError:
                    pass

        # Ordenar de mayor a menor
        ordenados = sorted(
            puntajes.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return render_template(
            "riasec_resultado.html",
            puntajes=puntajes,
            ordenados=ordenados
        )

    return render_template("riasec.html")

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

