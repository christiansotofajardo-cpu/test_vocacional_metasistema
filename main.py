from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# REGISTRO
# -------------------------------
@app.route("/registro")
def registro():
    return render_template("registro.html")


# -------------------------------
# TEST RIASEC (formulario)
# -------------------------------
@app.route("/test/riasec")
def test_riasec():
    return render_template("riasec.html")


# -------------------------------
# RESULTADO RIASEC (CÁLCULO REAL)
# -------------------------------
@app.route("/test/riasec_resultado")
def riasec_resultado():
    # 1. Inicializar puntajes
    puntajes = {
        "R": 0,
        "I": 0,
        "A": 0,
        "S": 0,
        "E": 0,
        "C": 0
    }

    # 2. Leer respuestas desde la URL (?R1=2&R2=3...)
    for key, value in request.args.items():
        try:
            letra = key[0].upper()   # R1 -> R
            puntajes[letra] += int(value)
        except:
            continue

    # 3. Ordenar de mayor a menor
    ordenados = sorted(
        puntajes.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 4. Enviar EXACTAMENTE lo que el template espera
    return render_template(
        "riasec_resultado.html",
        ordenados=ordenados
    )


# -------------------------------
# AUTOEFICACIA (placeholder)
# -------------------------------
@app.route("/test/autoeficacia")
def autoeficacia():
    return render_template("autoeficacia.html")


@app.route("/test/autoeficacia_resultado")
def autoeficacia_resultado():
    return render_template("autoeficacia_resultado.html")


# -------------------------------
# CIERRE
# -------------------------------
@app.route("/cierre")
def cierre():
    return render_template("cierre.html")


# -------------------------------
# ADMIN (si lo usas)
# -------------------------------
@app.route("/admin")
def admin():
    return render_template("admin.html")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
