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
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        correo = request.form.get("correo")
        establecimiento = request.form.get("establecimiento")
        curso = request.form.get("curso")
        consent = request.form.get("consent")

        # Validación mínima
        if not consent:
            return render_template(
                "registro.html",
                error="Debes aceptar el consentimiento informado para continuar."
            )

        # En esta versión NO guardamos datos
        # Solo avanzamos en el flujo
        return redirect(url_for("riasec"))

    return render_template("registro.html")

# -------------------------
# RIASEC
# -------------------------
@app.route("/test/riasec", methods=["GET", "POST"])
def riasec():
    if request.method == "POST":
        # Leer respuestas RIASEC (por ahora sin persistencia)
        respuestas = dict(request.form)

        # Placeholder de cierre de módulo
        return render_template(
            "mensaje.html",
            titulo="RIASEC completado",
            mensaje=(
                "Has respondido correctamente el Inventario de Intereses Vocacionales. "
                "En la siguiente etapa se incorporará el módulo de Autoeficacia."
            )
        )

    return render_template("riasec.html")

# -------------------------
# Página genérica de mensaje
# -------------------------
@app.get("/mensaje")
def mensaje():
    return render_template(
        "mensaje.html",
        titulo="Proceso en curso",
        mensaje="Este es un mensaje de sistema."
    )

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

