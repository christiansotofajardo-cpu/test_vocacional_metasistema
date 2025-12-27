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
        # Por ahora solo leemos los datos (sin guardar)
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        correo = request.form.get("correo")
        establecimiento = request.form.get("establecimiento")
        curso = request.form.get("curso")
        consent = request.form.get("consent")

        # Si falta consentimiento, volvemos al registro
        if not consent:
            return render_template("registro.html", error="Debes aceptar el consentimiento.")

        # Siguiente paso del flujo (placeholder)
        return redirect(url_for("riasec_intro"))

    return render_template("registro.html")

# -------------------------
# RIASEC (intro placeholder)
# -------------------------
@app.get("/test/riasec")
def riasec_intro():
    return (
        "<h1>RIASEC</h1>"
        "<p>Aquí comienza el Inventario de Intereses Vocacionales (60 ítems).</p>"
        "<p>Este es un placeholder para el siguiente paso.</p>"
        "<a href='/'>Volver al inicio</a>"
    )

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
