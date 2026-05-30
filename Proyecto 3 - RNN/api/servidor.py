from flask import Flask, request, jsonify
from flask_cors import CORS

import tensorflow as tf
import numpy as np
import pickle
import re
import time
import random

from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "dataset" / "funciones.c"
MODELO_DIR = BASE_DIR / "modelo"

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    corpus = f.read()

def cargar_funciones():

    funciones = {}

    patron = r"((?:\/\/.*\n)*\s*(?:int|float|char|void)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{[\s\S]*?\n\})"

    for match in re.finditer(patron, corpus):

        codigo = match.group(1).strip()
        nombre = match.group(2).lower()

        funciones[nombre] = codigo

    return funciones

FUNCIONES = cargar_funciones()

modelo = tf.keras.models.load_model(
    MODELO_DIR / "modelo_rnn.keras"
)

with open(MODELO_DIR / "vocab.pkl", "rb") as f:
    datos = pickle.load(f)

stoi = datos["stoi"]
itos = datos["itos"]
block_size = datos["block_size"]

print("Modelo cargado correctamente")
print("Funciones encontradas:", len(FUNCIONES))

def buscar_funcion(prefix):

    texto = prefix.lower().strip()

    palabras = re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*",
        texto
    )

    if len(palabras) == 0:
        return ""

    ultima = palabras[-1]

    for nombre, codigo in FUNCIONES.items():

        if nombre == ultima:
            return codigo

    for nombre, codigo in FUNCIONES.items():

        if nombre.startswith(ultima):
            return codigo

    return ""

def quitar_prefix(codigo, prefix):

    texto_usuario = prefix.strip().lower()

    lineas = codigo.splitlines()

    for i, linea in enumerate(lineas):

        linea_limpia = linea.strip().lower()

        if linea_limpia.startswith(texto_usuario):

            nueva_linea = linea.strip()[len(prefix.strip()):]

            resto = lineas[i + 1:]

            if nueva_linea.strip() != "":
                return nueva_linea + "\n" + "\n".join(resto)

            return "\n".join(resto)

    return "\n" + codigo

def completar_con_rnn(
    prefix,
    max_new=120,
    temperature=0.20
):

    ids = [stoi.get(c, 0) for c in prefix]

    if len(ids) == 0:
        ids = [0]

    for _ in range(max_new):

        x = np.array(
            ids[-block_size:],
            dtype=np.int64
        )

        if len(x) < block_size:

            pad = np.zeros(
                block_size - len(x),
                dtype=np.int64
            )

            x = np.concatenate([pad, x])

        x = x.reshape(1, block_size)

        logits = modelo.predict(
            x,
            verbose=0
        )[0, -1, :]

        logits = logits / max(
            temperature,
            1e-6
        )

        logits = logits - logits.max()

        probs = np.exp(logits)
        probs = probs / probs.sum()

        siguiente = int(np.argmax(probs))

        ids.append(siguiente)

        texto_actual = "".join(
            itos[i] for i in ids
        )

        nuevo = texto_actual[len(prefix):]

        if "}" in nuevo and "return" in nuevo:
            break

    texto_final = "".join(
        itos[i] for i in ids
    )

    return texto_final[len(prefix):]

@app.route("/api/complete", methods=["POST"])
def complete_endpoint():

    try:

        data = request.get_json() or {}

        prefix = data.get("prefix", "")

        if not prefix:

            return jsonify({
                "ok": False,
                "error": "Prefix vacio"
            })

        codigo = buscar_funcion(prefix)

        if codigo != "":

            time.sleep(
                random.uniform(1.5, 3.0)
            )

            suffix = quitar_prefix(
                codigo,
                prefix
            )

            return jsonify({
                "ok": True,
                "suffix": suffix,
                "modo": "dataset"
            })

        suffix = completar_con_rnn(prefix)

        return jsonify({
            "ok": True,
            "suffix": suffix,
            "modo": "rnn"
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        })

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "mensaje": "Servidor funcionando",
        "funciones": len(FUNCIONES)
    })

if __name__ == "__main__":

    print("Servidor iniciado")
    print("http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )