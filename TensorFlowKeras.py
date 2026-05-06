import numpy as np
import tensorflow as tf

# Semilla para resultados reproducibles
tf.keras.utils.set_random_seed(42)

# =========================
# CORPUS DE ENTRENAMIENTO
# =========================

CORPUS = r'''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distancia_origen(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

for i in range(10):
    print(i, fibonacci(i))
'''

# =========================
# VOCABULARIO
# =========================

chars = sorted(set(CORPUS))

stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

VOCAB_SIZE = len(chars)

def encode(s):
    return [stoi[c] for c in s]

def decode(ids):
    return "".join(itos[i] for i in ids)

SEQ = np.array(encode(CORPUS), dtype=np.int64)

# =========================
# PREPARACIÓN DE DATOS
# =========================

block_size_tf = 64

X_rows_tf = []
Y_rows_tf = []

for i in range(0, len(SEQ) - block_size_tf):

    X_rows_tf.append(
        SEQ[i : i + block_size_tf]
    )

    Y_rows_tf.append(
        SEQ[i + 1 : i + 1 + block_size_tf]
    )

X_tf = np.stack(X_rows_tf)
Y_tf = np.stack(Y_rows_tf)

# =========================
# MODELO LSTM
# =========================

embed_dim_tf = 48
hidden_tf = 64

model_tf = tf.keras.Sequential(
    [

        tf.keras.layers.Input(
            shape=(block_size_tf,)
        ),

        tf.keras.layers.Embedding(
            VOCAB_SIZE,
            embed_dim_tf
        ),

        tf.keras.layers.LSTM(
            hidden_tf,
            return_sequences=True
        ),

        tf.keras.layers.TimeDistributed(
            tf.keras.layers.Dense(VOCAB_SIZE)
        ),
    ]
)

# =========================
# COMPILACIÓN
# =========================

model_tf.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),

    loss=tf.keras.losses.SparseCategoricalCrossentropy(
        from_logits=True
    ),
)

# =========================
# RESUMEN DEL MODELO
# =========================

model_tf.summary()

# =========================
# ENTRENAMIENTO
# =========================

history = model_tf.fit(
    X_tf,
    Y_tf,
    epochs=120,
    batch_size=16,
    verbose=1,
)

# =========================
# RESULTADOS
# =========================

print("\nEntrenamiento terminado")
print("épocas:", len(history.history["loss"]))
print("pérdida inicial:", float(history.history["loss"][0]))
print("pérdida final:", float(history.history["loss"][-1]))

# =========================
# GENERADOR DE TEXTO
# =========================

def complete_tf(
    prompt,
    max_new_tokens=120,
    temperature=0.8
):

    ids = encode(prompt)

    for _ in range(max_new_tokens):

        x = np.array(
            ids[-block_size_tf:],
            dtype=np.int64
        )

        # Padding si faltan caracteres
        if x.shape[0] < block_size_tf:

            pad = np.full(
                block_size_tf - x.shape[0],
                ids[0],
                dtype=np.int64
            )

            x = np.concatenate([pad, x])

        x = x.reshape(1, block_size_tf)

        logits = model_tf(
            x,
            training=False
        ).numpy()[0, -1, :]

        # Temperatura
        logits = logits / max(temperature, 1e-6)

        logits = logits - logits.max()

        probs = np.exp(logits)

        probs = probs / probs.sum()

        next_id = int(
            np.random.choice(
                len(probs),
                p=probs
            )
        )

        ids.append(next_id)

    return decode(ids)

# =========================
# PRUEBA
# =========================

resultado = complete_tf(
    "def fac",
    max_new_tokens=150,
    temperature=0.75
)

print("\n===== TEXTO GENERADO =====\n")
print(resultado)