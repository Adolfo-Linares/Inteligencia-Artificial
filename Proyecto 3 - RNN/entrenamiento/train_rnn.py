import os
import json
import numpy as np
import tensorflow as tf

tf.keras.utils.set_random_seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "funciones.c")
MODELO_DIR = os.path.join(BASE_DIR, "modelo")

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    corpus = f.read()

chars = sorted(set(corpus))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
VOCAB_SIZE = len(chars)

SEQ = np.array([stoi[c] for c in corpus], dtype=np.int64)

BLOCK_SIZE = 64

X_rows = []
Y_rows = []

for i in range(0, len(SEQ) - BLOCK_SIZE):
    X_rows.append(SEQ[i:i + BLOCK_SIZE])
    Y_rows.append(SEQ[i + 1:i + 1 + BLOCK_SIZE])

X = np.stack(X_rows)
Y = np.stack(Y_rows)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(BLOCK_SIZE,)),
    tf.keras.layers.Embedding(VOCAB_SIZE, 64),
    tf.keras.layers.SimpleRNN(
        128,
        activation="tanh",
        return_sequences=True,
        dropout=0.1
    ),
    tf.keras.layers.TimeDistributed(
        tf.keras.layers.Dense(VOCAB_SIZE)
    )
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
)

model.summary()

history = model.fit(
    X,
    Y,
    epochs=120,
    batch_size=32,
    verbose=1
)

os.makedirs(MODELO_DIR, exist_ok=True)

model.save(os.path.join(MODELO_DIR, "asistente.keras"))

meta = {
    "block_size": BLOCK_SIZE,
    "chars": chars
}

with open(os.path.join(MODELO_DIR, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False)

print("Entrenamiento terminado")
print("VOCAB_SIZE:", VOCAB_SIZE)
print("Caracteres:", len(corpus))
print("Perdida final:", history.history["loss"][-1])
