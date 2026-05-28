import os
import csv
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

# Opcional: para graficar los datos en 2D y 3D
import matplotlib
# Configuramos backend para ventanas interactivas (TkAgg funciona en la mayoría de sistemas)
try:
    matplotlib.use("TkAgg")
except Exception:
    try:
        matplotlib.use("Qt5Agg")
    except Exception:
        pass  # Usa el backend por defecto
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, necesario para activar 3D en matplotlib

# Activamos modo interactivo para que las ventanas no bloqueen el juego
plt.ion()


# Ventana base y factor de escala
BASE_W, BASE_H = 1080, 720
WINDOW_FRACTION = 0.97
EXTRA_SCALE = 1.1


@dataclass
class Sample:
    velocidad_bala: float
    distancia: float
    altura_bala: float   # altura relativa de la bala (0.0=suelo, 1.0=nivel medio-cuerpo)
    accion: int  # 0=nada/de pie, 1=saltar, 2=agacharse
    tiempo_bala: int = 0  # frame desde que se disparó la bala; sirve para aprender patrones repetidos


class Juego:
    def __init__(self) -> None:
        pygame.init()

        # Ventana fija (sin redimensionamiento automático) para evitar
        # problemas en pantallas muy grandes / 2K / 4K.
        self._flags = 0
        self._fullscreen = False

        # Tamaño fijo de ventana
        start_w = BASE_W
        start_h = BASE_H
        self.pantalla = pygame.display.set_mode((start_w, start_h), self._flags)
        pygame.display.set_caption("Juego: Bala + salto + MLP (solo memoria)")

        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AMARILLO = (255, 220, 120)

        # Estado global
        self.corriendo = True
        self.modo_auto = False

        # Datos / modelo
        self.datos_modelo: List[Sample] = []
        self.modelo: Optional[MLPClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.modelo_entrenado = False
        # Caso especial: cuando solo hay una clase en los datos
        # (0 = nunca salto, 1 = siempre salto).
        self.clase_unica: Optional[int] = None
        # Debug / info del modelo en tiempo real
        self.ultima_proba_salto: Optional[float] = None

        # Parámetros de decisión
        self.decision_window = 500
        # Para aprender patrones repetidos como agacharse/pararse/agacharse
        # necesitamos guardar CADA frame, no solo cuando la bala está cerca.
        self.decision_record_every = 1
        self._decision_frame_counter = 0
        self.frame_bala = 0
        self.patrones_auto = {}  # {altura_bala: {tiempo_bala: accion_mas_repetida}}
        # Saltos guardados como EVENTOS por tiempo. Esto permite copiar varios saltos
        # aunque sean intentos repetidos durante una misma bala.
        self.saltos_auto = {}  # {altura_bala: [tiempos_donde_presionaste_espacio]}
        self._auto_saltos_hechos = set()
        self._auto_salto_pendiente_evento = None
        self._auto_salto_evento_actual = None
        # Distancia promedio donde el usuario PRESIONÓ salto por cada tipo de bala.
        # Esto corrige el problema de saltar tarde/temprano cuando cambia la velocidad.
        self.salto_trigger_distancia = {}
        self._auto_salto_usado_en_bala = False
        # Evita que un solo tramo continuo de SALTAR produzca muchos saltos.
        # El salto solo se dispara cuando la acción cambia de NO saltar -> saltar.
        self._auto_salto_bloqueado = False
        self._ultima_accion_auto = 0
        # Cooldown para que un mismo frame/evento de salto no se repita muchas veces.
        # Pero sí permite saltar otra vez después si así lo entrenaste.
        self._auto_salto_cooldown = 0

        # Geometría / física (se rellenan en _apply_resolution)
        self.w, self.h = start_w, start_h
        self.scale = 1.0
        self.margin = 50
        self.ground_y = self.h - 100
        self.player_size = (32, 48)
        self.bullet_size = (16, 16)
        self.ship_size = (64, 64)
        # Velocidad de desplazamiento del fondo
        self.fondo_speed = 3

        self.salto = False
        self.agachado = False
        # Se activa solo en el frame donde el usuario PRESIONA espacio.
        # Sirve para entrenar el impulso de salto, no todos los frames en el aire.
        self.salto_pulsado = False
        self.en_suelo = True
        self.salto_vel_inicial = 15.0
        self.gravedad = 1.0
        self.salto_vel = self.salto_vel_inicial

        self.current_frame = 0
        self.frame_speed = 10
        self.frame_count = 0

        # Velocidad base de la bala (en píxeles/frame, negativa porque va de der→izq)
        self.velocidad_bala = -12
        self.bala_disparada = False
        # Altura relativa de la bala: 0.0 = nivel suelo, 1.0 = nivel medio-cuerpo
        self.altura_bala_relativa = 0.0
        self.fondo_x1 = 0
        self.fondo_x2 = start_w

        self._apply_resolution(start_w, start_h, reset_positions=True)
        self._reset_estado_juego()

    # ----------------- resolución / assets -----------------
    def _apply_resolution(self, w: int, h: int, reset_positions: bool) -> None:
        self.w, self.h = int(w), int(h)

        self.scale = min(self.w / BASE_W, self.h / BASE_H) * EXTRA_SCALE
        self.scale = max(1.0, self.scale)

        self.margin = int(50 * self.scale)
        ground_offset = int(100 * self.scale)
        self.ground_y = self.h - ground_offset

        self.player_size = (int(32 * self.scale), int(48 * self.scale))
        self.player_size_agachado = (int(32 * self.scale), int(24 * self.scale))  # mitad de altura
        self.bullet_size = (int(16 * self.scale), int(16 * self.scale))
        self.ship_size = (int(64 * self.scale), int(64 * self.scale))
        self.fondo_speed = max(1, int(2 * self.scale))

        self.salto_vel_inicial = 15 * self.scale
        self.gravedad = 1 * self.scale
        self.salto_vel = self.salto_vel_inicial
        # Altura media del cuerpo del jugador (para que la bala apunte aquí)
        self.bala_altura_media = int(self.player_size[1] // 2)

        self.decision_window = int(500 * self.scale)

        self.fuente = pygame.font.SysFont("Arial", int(24 * self.scale))
        self.fuente_chica = pygame.font.SysFont("Arial", int(18 * self.scale))

        self._cargar_assets()

        if reset_positions or not hasattr(self, "jugador"):
            self.jugador = pygame.Rect(self.margin, self.ground_y, self.player_size[0], self.player_size[1])
            self.bala = pygame.Rect(
                self.w - self.margin,
                self.ground_y + int(10 * self.scale),
                self.bullet_size[0],
                self.bullet_size[1],
            )
            self.nave = pygame.Rect(
                self.w - int(100 * self.scale),
                self.ground_y,
                self.ship_size[0],
                self.ship_size[1],
            )

    def _cargar_assets(self) -> None:
        def safe_load(path: str, size: Tuple[int, int], fallback_color=(200, 200, 200, 255)) -> pygame.Surface:
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            except Exception:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                surf.fill(fallback_color)
                return surf

        base = os.path.dirname(__file__)
        self.jugador_frames = [
            safe_load(os.path.join(base, "assets/sprites/mono.png"), self.player_size),
            safe_load(os.path.join(base, "assets/sprites/mono.png"), self.player_size),
            safe_load(os.path.join(base, "assets/sprites/mono.png"), self.player_size),
            safe_load(os.path.join(base, "assets/sprites/mono.png"), self.player_size),
        ]
        self.bala_img = safe_load(
            os.path.join(base, "assets/sprites/purple_ball.png"),
            self.bullet_size,
            (160, 120, 255, 255),
        )
        self.fondo_img = safe_load(
            os.path.join(base, "assets/game/fondo2.png"),
            (self.w, self.h),
            (40, 40, 40, 255),
        )
        self.nave_img = safe_load(
            os.path.join(base, "assets/game/cannon.png"),
            self.ship_size,
            (140, 255, 200, 255),
        )

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            info = pygame.display.Info()
            w = info.current_w or self.w
            h = info.current_h or self.h
            self.pantalla = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
            self._apply_resolution(w, h, reset_positions=True)
        else:
            # Volver a ventana fija BASE_W x BASE_H
            self.pantalla = pygame.display.set_mode((BASE_W, BASE_H), self._flags)
            self._apply_resolution(BASE_W, BASE_H, reset_positions=True)
        self._reset_estado_juego()

    # ----------------- estado juego / modelo -----------------
    def _reset_estado_juego(self) -> None:
        self.jugador.x, self.jugador.y = self.margin, self.ground_y
        self.jugador.height = self.player_size[1]
        self.nave.x, self.nave.y = self.w - int(100 * self.scale), self.ground_y
        self.bala.x = self.w - self.margin
        self.bala.y = self.ground_y + int(10 * self.scale)
        self.bala_disparada = False
        self.altura_bala_relativa = 0.0
        self.velocidad_bala = int(-10 * self.scale)
        self.salto = False
        self.agachado = False
        self.salto_pulsado = False
        self.en_suelo = True
        self.salto_vel = self.salto_vel_inicial
        self._decision_frame_counter = 0
        self.frame_bala = 0
        self._auto_salto_bloqueado = False
        self._ultima_accion_auto = 0
        self._auto_salto_cooldown = 0
        self._auto_saltos_hechos = set()
        self._auto_salto_pendiente_evento = None
        self._auto_salto_evento_actual = None
        self.fondo_x1 = 0
        self.fondo_x2 = self.w

    def _reset_modelo(self) -> None:
        self.modelo = None
        self.scaler = None
        self.modelo_entrenado = False
        self.clase_unica = None
        self.patrones_auto = {}
        self.saltos_auto = {}
        self.salto_trigger_distancia = {}

    # ----------------- export / gráficas -----------------

    def exportar_datos_csv(self) -> str:
        """
        Exporta el contenido de self.datos_modelo a un CSV sencillo.
        Devuelve un mensaje con la ruta del archivo o el motivo del fallo.
        """
        if not self.datos_modelo:
            return "No hay datos para exportar."

        base = os.path.dirname(__file__)
        ruta = os.path.join(base, "datos_mlp.csv")

        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["velocidad_bala", "distancia", "altura_bala", "tiempo_bala", "accion"])
                for s in self.datos_modelo:
                    writer.writerow([s.velocidad_bala, s.distancia, s.altura_bala, s.tiempo_bala, s.accion])
        except Exception as e:
            return f"Error al guardar CSV: {e}"

        return f"CSV guardado en datos_mlp.csv ({len(self.datos_modelo)} filas)."

    def graficar_datos_2d(self) -> str:
        """
        Grafica velocidad_bala vs distancia en 2D,
        coloreando por salto (0 / 1).
        Abre una ventana interactiva (desde el hilo principal, no bloqueante).
        """
        if not self.datos_modelo:
            return "No hay datos para graficar."

        xs = [s.distancia for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]
        color_map = {0: "blue", 1: "red", 2: "green"}
        cs = [color_map.get(s.accion, "gray") for s in self.datos_modelo]

        # Cerrar figura anterior si existe para evitar acumulación
        fig_num = plt.figure("Datos MLP - 2D", figsize=(8, 6)).number
        plt.figure(fig_num)
        plt.clf()

        ax = plt.gca()
        ax.scatter(xs, ys, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia jugador-bala")
        ax.set_ylabel("Velocidad bala")
        ax.set_title("Datos MLP (azul=nada, rojo=salto, verde=agacha)")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show(block=False)
        plt.draw()

        return "Mostrando gráfica 2D interactiva (puedes rotar/zoom)."

    def graficar_datos_3d(self) -> str:
        """
        Grafica velocidad_bala vs distancia vs índice de tiempo (frame) en 3D,
        coloreando por salto (0 / 1).
        Abre una ventana interactiva (desde el hilo principal, no bloqueante).
        """
        if not self.datos_modelo:
            return "No hay datos para graficar."

        xs = [s.distancia for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]
        zs = [s.altura_bala for s in self.datos_modelo]
        color_map = {0: "blue", 1: "red", 2: "green"}
        cs = [color_map.get(s.accion, "gray") for s in self.datos_modelo]

        # Cerrar figura anterior si existe para evitar acumulación
        fig = plt.figure("Datos MLP - 3D", figsize=(8, 6))
        plt.clf()

        # Crear eje 3D correctamente desde la figura
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(xs, ys, zs, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia")
        ax.set_ylabel("Velocidad bala")
        ax.set_zlabel("Altura bala")
        ax.set_title("Datos MLP 3D (azul=nada, rojo=salto, verde=agacha)")
        plt.tight_layout()
        plt.show(block=False)
        plt.draw()

        return "Mostrando gráfica 3D interactiva (puedes rotar/zoom)."

    # ----------------- bala / salto / agacharse -----------------
    def disparar_bala(self) -> None:
        if not self.bala_disparada:
            # Velocidad aleatoria
            self.velocidad_bala = int(random.randint(-12, -6) * self.scale)
            # Altura aleatoria: 0 = suelo (hay que saltar), 1 = nivel medio (hay que agacharse)
            self.altura_bala_relativa = random.choice([0.0, 1.0])
            if self.altura_bala_relativa == 0.0:
                # Bala a ras del suelo
                self.bala.y = self.ground_y + int(10 * self.scale)
            else:
                # Bala a mitad de cuerpo (nivel medio — hay que agacharse)
                self.bala.y = self.ground_y - self.bala_altura_media + int(14 * self.scale)
            self.bala_disparada = True
            self.frame_bala = 0
            self._auto_salto_bloqueado = False
            self._auto_salto_usado_en_bala = False
            self._ultima_accion_auto = 0
            self._auto_saltos_hechos = set()
            self._auto_salto_pendiente_evento = None
            self._auto_salto_evento_actual = None

    def reset_bala(self) -> None:
        self.bala.x = self.w - self.margin
        self.bala_disparada = False
        self.frame_bala = 0
        self._auto_salto_bloqueado = False
        self._auto_salto_usado_en_bala = False
        self._ultima_accion_auto = 0
        self._auto_salto_cooldown = 0
        self._auto_saltos_hechos = set()
        self._auto_salto_pendiente_evento = None
        self._auto_salto_evento_actual = None

    def iniciar_salto(self) -> None:
        if self.en_suelo and not self.agachado:
            self.salto = True
            self.en_suelo = False

    def iniciar_agacharse(self) -> None:
        """Activa el estado agachado (solo si está en suelo y no saltando)."""
        if self.en_suelo and not self.salto:
            if not self.agachado:
                self.agachado = True
                # Encogemos el rect del jugador y lo bajamos para que quede pegado al suelo
                self.jugador.height = self.player_size_agachado[1]
                self.jugador.y = self.ground_y + (self.player_size[1] - self.player_size_agachado[1])

    def terminar_agacharse(self) -> None:
        """Desactiva el estado agachado."""
        if self.agachado:
            self.agachado = False
            self.jugador.height = self.player_size[1]
            self.jugador.y = self.ground_y

    def manejar_salto(self) -> None:
        if self.salto:
            self.jugador.y -= int(self.salto_vel)
            self.salto_vel -= self.gravedad
            if self.jugador.y >= self.ground_y:
                self.jugador.y = self.ground_y
                self.jugador.height = self.player_size[1]
                self.salto = False
                self.salto_vel = self.salto_vel_inicial
                self.en_suelo = True


    # ----------------- datos / ML -----------------
    def registrar_decision_manual(self) -> None:
        """Guarda el patrón completo por frames.

        Esto permite que el automático copie cosas como:
        agacharse/pararse/agacharse repetidamente o saltar repetidamente.
        Aquí SÍ guardamos la acción 0 porque significa "levantarse / no hacer nada"
        y es necesaria para copiar el reboteo.
        """
        if not self.bala_disparada:
            return

        self._decision_frame_counter += 1
        if self._decision_frame_counter % self.decision_record_every != 0:
            return

        distancia = abs(self.jugador.x - self.bala.x)

        # IMPORTANTE:
        # El salto se guarda solo cuando se presiona ESPACIO, no durante
        # todos los frames que el personaje permanece en el aire.
        # Así el auto no brinca de más al caer.
        if self.salto_pulsado:
            accion = 1
        elif self.agachado:
            accion = 2
        else:
            accion = 0

        self.salto_pulsado = False

        self.datos_modelo.append(
            Sample(
                velocidad_bala=float(self.velocidad_bala),
                distancia=float(distancia),
                altura_bala=float(self.altura_bala_relativa),
                accion=accion,
                tiempo_bala=int(self.frame_bala),
            )
        )

    def _crear_patrones_auto(self, samples: List[Sample]) -> None:
        """Crea patrones por tiempo y guarda los saltos como eventos.

        Cambio importante:
        - AGACHARSE y NADA se guardan como estado por frame.
        - SALTAR se guarda como evento por tiempo, no como estado.
        Esto evita que el MLP ignore tus saltos repetidos o que los confunda con
        estar en el aire.
        """
        from collections import defaultdict, Counter

        votos = defaultdict(Counter)
        saltos = {0: [], 1: []}

        for s in samples:
            altura = int(round(s.altura_bala))
            tiempo = int(s.tiempo_bala)
            accion = int(s.accion)

            if accion == 1:
                saltos.setdefault(altura, []).append(tiempo)
                # No metemos el salto a la tabla de estados; se maneja aparte.
                continue

            votos[(altura, tiempo)][accion] += 1

        patrones = {0: {}, 1: {}}
        for (altura, tiempo), contador in votos.items():
            patrones.setdefault(altura, {})[tiempo] = contador.most_common(1)[0][0]

        # Agrupar saltos cercanos para no duplicar un mismo apretón de tecla,
        # pero conservar saltos repetidos separados.
        saltos_limpios = {0: [], 1: []}
        for altura, tiempos in saltos.items():
            tiempos = sorted(tiempos)
            for t in tiempos:
                if not saltos_limpios[altura] or abs(t - saltos_limpios[altura][-1]) >= 3:
                    saltos_limpios[altura].append(t)

        self.patrones_auto = patrones
        self.saltos_auto = saltos_limpios

        # También guardamos distancia de referencia por si quieres usarla después.
        self.salto_trigger_distancia = {}
        for altura in (0, 1):
            distancias_salto = sorted(
                float(s.distancia)
                for s in samples
                if int(round(s.altura_bala)) == altura and int(s.accion) == 1
            )
            if distancias_salto:
                mid = len(distancias_salto) // 2
                if len(distancias_salto) % 2 == 1:
                    mediana = distancias_salto[mid]
                else:
                    mediana = (distancias_salto[mid - 1] + distancias_salto[mid]) / 2
                self.salto_trigger_distancia[altura] = mediana

    def entrenar_modelo(self) -> Tuple[bool, str]:
        """Entrena sin obligarte a tener 2 acciones diferentes.

        Si solo entrenaste "no hacer nada", guarda ese patrón y en AUTO no hará nada.
        Si entrenaste saltos repetidos, los copia como eventos por tiempo.
        Si entrenaste agacharse/pararse, también copia ese reboteo.
        """
        samples = list(self.datos_modelo)

        if len(samples) < 20:
            return False, "Necesitas mínimo 20 muestras en modo MANUAL."

        conteo_original = {
            0: sum(1 for s in samples if s.accion == 0),
            1: sum(1 for s in samples if s.accion == 1),
            2: sum(1 for s in samples if s.accion == 2),
        }

        clases_presentes = [c for c, n in conteo_original.items() if n > 0]

        # Siempre creamos patrones, aunque solo exista una acción.
        self._crear_patrones_auto(samples)

        # Si solo hay una acción, no entrenamos MLP porque sklearn necesita mínimo 2 clases.
        # Aun así queda ENTRENADO porque el patrón sí se puede reproducir.
        if len(clases_presentes) == 1:
            self.modelo = None
            self.scaler = None
            self.modelo_entrenado = True
            self.clase_unica = int(clases_presentes[0])
            nombres = {0: "ENTRENADO", 1: "SALTAR", 2: "AGACHARSE"}
            return True, f"Patrón guardado: {nombres.get(self.clase_unica, '?')}"

        # MLP como respaldo cuando no haya patrón exacto.
        grupos = {c: [s for s in samples if s.accion == c] for c in clases_presentes}

        # No eliminamos totalmente NADA porque también significa levantarse.
        # Solo la reducimos un poco si domina demasiado.
        movimientos = len(grupos.get(1, [])) + len(grupos.get(2, []))
        if 0 in grupos and movimientos > 0:
            limite_nada = max(20, int(movimientos * 0.80))
            if len(grupos[0]) > limite_nada:
                grupos[0] = random.sample(grupos[0], limite_nada)

        max_cantidad = max(len(v) for v in grupos.values())
        samples_balanceados = []
        for c, grupo in grupos.items():
            grupo_balanceado = list(grupo)
            while len(grupo_balanceado) < max_cantidad:
                grupo_balanceado.append(random.choice(grupo))
            samples_balanceados.extend(grupo_balanceado)

        random.shuffle(samples_balanceados)

        X = [
            [s.velocidad_bala, s.distancia, s.altura_bala, s.tiempo_bala]
            for s in samples_balanceados
        ]
        y = [s.accion for s in samples_balanceados]

        try:
            conteo_y = {c: y.count(c) for c in set(y)}
            stratify_y = y if min(conteo_y.values()) >= 2 else None

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                stratify=stratify_y,
            )

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            clf = MLPClassifier(
                hidden_layer_sizes=(96, 48),
                activation="relu",
                solver="adam",
                max_iter=4000,
                random_state=42,
                early_stopping=True,
                n_iter_no_change=35,
            )

            clf.fit(X_train, y_train)
            acc = clf.score(X_test, y_test)

            self.scaler = scaler
            self.modelo = clf
            self.modelo_entrenado = True
            self.clase_unica = None

            return True, f"Patrones + MLP | acc={acc:.2f}"

        except Exception as e:
            # Aunque falle el MLP, dejamos los patrones funcionando.
            self.modelo = None
            self.scaler = None
            self.modelo_entrenado = True
            self.clase_unica = None
            return True, f"Patrones guardados | MLP no usado"

    def decision_auto(self) -> int:
        """Retorna la acción automática: 0=de pie, 1=saltar, 2=agacharse.

        Versión más fuerte para saltos:
        - Los saltos se copian como EVENTOS por tiempo.
        - Si presionaste espacio varias veces entrenando, guarda esos intentos.
        - Si el personaje todavía está en el aire, deja el salto pendiente y lo hace
          apenas toque el suelo.
        - No depende tanto del MLP para saltar; primero usa los eventos guardados.
        """
        if not self.modelo_entrenado:
            return 0
        if not self.bala_disparada:
            return 0

        altura = int(round(self.altura_bala_relativa))
        tiempo = int(self.frame_bala)
        distancia = abs(self.jugador.x - self.bala.x)

        # =========================================================
        # 1) Saltos como eventos entrenados
        # =========================================================
        eventos_salto = self.saltos_auto.get(altura, [])

        if eventos_salto:
            margen_antes = 4
            margen_despues = 90

            # Si quedó un salto pendiente porque estabas en el aire,
            # ejecútalo apenas el personaje toque el suelo.
            if (
                self._auto_salto_pendiente_evento is not None
                and self._auto_salto_pendiente_evento not in self._auto_saltos_hechos
                and self.en_suelo
                and not self.agachado
                and self._auto_salto_cooldown <= 0
            ):
                self._auto_salto_evento_actual = self._auto_salto_pendiente_evento
                return 1

            for i, t_salto in enumerate(eventos_salto):
                evento_id = (altura, i)

                if evento_id in self._auto_saltos_hechos:
                    continue

                # Si ya pasó el tiempo entrenado pero sigue dentro de una ventana
                # amplia, todavía intentamos hacerlo. Esto ayuda mucho cuando la bala
                # cambia de velocidad o el personaje estaba cayendo.
                if t_salto - margen_antes <= tiempo <= t_salto + margen_despues:
                    if self.en_suelo and not self.agachado and self._auto_salto_cooldown <= 0:
                        self._auto_salto_evento_actual = evento_id
                        return 1

                    # Si todavía no puede saltar, lo dejamos pendiente.
                    self._auto_salto_pendiente_evento = evento_id
                    return 0

            # Refuerzo de seguridad: si sí entrenaste saltos para bala baja y la bala
            # ya está cerca, salta aunque el evento exacto no haya coincidido.
            if altura == 0 and self.en_suelo and not self.agachado and self._auto_salto_cooldown <= 0:
                if distancia <= self.decision_window * 0.85:
                    return 1

        # =========================================================
        # 2) Agacharse / levantarse como patrón por frame
        # =========================================================
        patron_altura = self.patrones_auto.get(altura, {})
        if patron_altura:
            if tiempo in patron_altura:
                accion_patron = int(patron_altura[tiempo])
            else:
                cercano = min(patron_altura.keys(), key=lambda t: abs(t - tiempo))
                accion_patron = int(patron_altura[cercano]) if abs(cercano - tiempo) <= 5 else 0

            # Si el patrón dice saltar, lo tratamos como evento y no como estado.
            if accion_patron == 1:
                if self.en_suelo and not self.agachado and self._auto_salto_cooldown <= 0:
                    return 1
                return 0

            return accion_patron

        # =========================================================
        # 3) Si solo entrenaste una acción
        # =========================================================
        if self.clase_unica is not None and self.modelo is None:
            accion = int(self.clase_unica)
            if accion == 1:
                if self._auto_salto_cooldown <= 0 and self.en_suelo and not self.agachado:
                    return 1
                return 0
            return accion

        # =========================================================
        # 4) Respaldo MLP
        # =========================================================
        if self.modelo is None or self.scaler is None:
            return 0

        X = [[
            float(self.velocidad_bala),
            float(distancia),
            float(self.altura_bala_relativa),
            float(self.frame_bala),
        ]]

        Xs = self.scaler.transform(X)
        accion = int(self.modelo.predict(Xs)[0])

        if hasattr(self.modelo, "predict_proba"):
            probas = self.modelo.predict_proba(Xs)[0]
            clases = list(self.modelo.classes_)
            self.ultima_proba_salto = float(probas[clases.index(1)]) if 1 in clases else 0.0
        else:
            self.ultima_proba_salto = 1.0 if accion == 1 else 0.0

        if accion == 1:
            if self._auto_salto_cooldown <= 0 and self.en_suelo and not self.agachado:
                return 1
            return 0

        return accion


     # ----------------- menú -----------------
    def _dibujar_menu(self, msg: str = "") -> None:
        # Fondo degradado oscuro
        for y in range(self.h):
            t = y / max(1, self.h)
            color = (
                int(10 + 22 * t),
                int(14 + 18 * t),
                int(32 + 55 * t),
            )
            pygame.draw.line(self.pantalla, color, (0, y), (self.w, y))

        # Decoración de fondo
        pygame.draw.circle(self.pantalla, (35, 70, 140), (int(self.w * 0.12), int(self.h * 0.18)), int(90 * self.scale), 2)
        pygame.draw.circle(self.pantalla, (80, 50, 140), (int(self.w * 0.88), int(self.h * 0.82)), int(120 * self.scale), 2)

        # Tamaño del panel; más alto para que nada se salga
        menu_w = min(int(self.w * 0.72), int(760 * self.scale))
        menu_h = min(int(self.h * 0.86), int(610 * self.scale))
        menu_x = self.w // 2 - menu_w // 2
        menu_y = self.h // 2 - menu_h // 2

        # Sombra del panel
        sombra_rect = pygame.Rect(menu_x + 10, menu_y + 12, menu_w, menu_h)
        pygame.draw.rect(self.pantalla, (0, 0, 0), sombra_rect, border_radius=int(22 * self.scale))

        # Panel principal
        panel = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        panel.fill((16, 18, 32, 235))
        self.pantalla.blit(panel, (menu_x, menu_y))

        pygame.draw.rect(
            self.pantalla,
            (95, 170, 255),
            (menu_x, menu_y, menu_w, menu_h),
            max(2, int(3 * self.scale)),
            border_radius=int(22 * self.scale),
        )

        # Barra superior
        barra_h = int(72 * self.scale)
        pygame.draw.rect(
            self.pantalla,
            (25, 35, 65),
            (menu_x, menu_y, menu_w, barra_h),
            border_radius=int(22 * self.scale),
        )
        pygame.draw.rect(
            self.pantalla,
            (25, 35, 65),
            (menu_x, menu_y + barra_h // 2, menu_w, barra_h // 2),
        )

        titulo_font = pygame.font.SysFont("Arial Black", max(28, int(38 * self.scale)))
        sub_font = pygame.font.SysFont("Arial", max(14, int(16 * self.scale)))

        titulo = titulo_font.render("MENÚ PRINCIPAL", True, self.BLANCO)
        self.pantalla.blit(titulo, (self.w // 2 - titulo.get_width() // 2, menu_y + int(12 * self.scale)))

        subtitulo = sub_font.render("Selecciona una opción con el teclado", True, (170, 195, 230))
        self.pantalla.blit(subtitulo, (self.w // 2 - subtitulo.get_width() // 2, menu_y + int(55 * self.scale)))

        opciones = [
            ("M", "Manual", "Jugar y guardar datos nuevos"),
            ("A", "Auto", "Usar el modelo entrenado"),
            ("T", "Entrenar", "Crear o actualizar el modelo MLP"),
            ("C", "CSV", "Exportar datos del entrenamiento"),
            ("F", "Pantalla", "Cambiar a pantalla completa"),
            ("Q", "Salir", "Cerrar el juego"),
        ]

        start_y = menu_y + int(105 * self.scale)
        row_h = int(58 * self.scale)
        gap = int(9 * self.scale)
        row_x = menu_x + int(48 * self.scale)
        row_w = menu_w - int(96 * self.scale)
        key_w = int(48 * self.scale)

        for i, (tecla, titulo_op, desc) in enumerate(opciones):
            y = start_y + i * (row_h + gap)
            row_rect = pygame.Rect(row_x, y, row_w, row_h)

            pygame.draw.rect(self.pantalla, (28, 32, 54), row_rect, border_radius=int(14 * self.scale))
            pygame.draw.rect(self.pantalla, (55, 70, 110), row_rect, 1, border_radius=int(14 * self.scale))

            key_rect = pygame.Rect(row_x + int(14 * self.scale), y + int(10 * self.scale), key_w, row_h - int(20 * self.scale))
            pygame.draw.rect(self.pantalla, (70, 125, 255), key_rect, border_radius=int(10 * self.scale))
            pygame.draw.rect(self.pantalla, (135, 180, 255), key_rect, 1, border_radius=int(10 * self.scale))

            letra = self.fuente.render(tecla, True, self.BLANCO)
            self.pantalla.blit(letra, (key_rect.centerx - letra.get_width() // 2, key_rect.centery - letra.get_height() // 2))

            txt_titulo = self.fuente.render(titulo_op, True, self.BLANCO)
            txt_desc = self.fuente_chica.render(desc, True, (160, 170, 195))
            tx = key_rect.right + int(18 * self.scale)
            self.pantalla.blit(txt_titulo, (tx, y + int(7 * self.scale)))
            self.pantalla.blit(txt_desc, (tx, y + int(34 * self.scale)))

        # Estado dentro del panel, sin salirse
        estado_y = start_y + len(opciones) * (row_h + gap) + int(12 * self.scale)
        estado_h = int(82 * self.scale)
        estado_rect = pygame.Rect(row_x, estado_y, row_w, estado_h)
        pygame.draw.rect(self.pantalla, (12, 15, 28), estado_rect, border_radius=int(14 * self.scale))
        pygame.draw.rect(self.pantalla, (55, 70, 110), estado_rect, 1, border_radius=int(14 * self.scale))

        estado = [
            f"Datos guardados: {len(self.datos_modelo)} muestras",
            f"Modelo: {'ENTRENADO' if self.modelo_entrenado else 'SIN ENTRENAR'}",
            f"Resolución: {self.w}x{self.h}",
        ]

        x_estado = estado_rect.x + int(18 * self.scale)
        y_estado = estado_rect.y + int(10 * self.scale)
        for line in estado:
            t = self.fuente_chica.render(line, True, (195, 205, 225))
            self.pantalla.blit(t, (x_estado, y_estado))
            y_estado += self.fuente_chica.get_linesize() + int(4 * self.scale)

        if msg:
            msg_rect = pygame.Rect(row_x, menu_y + menu_h - int(50 * self.scale), row_w, int(34 * self.scale))
            pygame.draw.rect(self.pantalla, (80, 55, 20), msg_rect, border_radius=int(10 * self.scale))
            aviso = self.fuente_chica.render(msg, True, (255, 225, 130))
            self.pantalla.blit(aviso, (msg_rect.centerx - aviso.get_width() // 2, msg_rect.centery - aviso.get_height() // 2))

        pygame.display.flip()

    def mostrar_menu(self) -> None:
        msg = ""
        esperando = True
        self._decision_frame_counter = 0
        while esperando and self.corriendo:
            self._dibujar_menu(msg)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False
                    esperando = False
                    break
                # Ya no reaccionamos a cambios de tamaño de ventana,
                # la ventana es fija.
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m:
                        self.modo_auto = False
                        self.datos_modelo.clear()
                        self._reset_modelo()
                        self._reset_estado_juego()
                        esperando = False
                        break
                    if e.key == pygame.K_a:
                        # Permitir entrar aunque no haya modelo entrenado
                        self.modo_auto = True
                        self._reset_estado_juego()

                        if not self.modelo_entrenado:
                            msg = "AUTO sin modelo: el personaje no reaccionará."

                        esperando = False
                        break
                    if e.key == pygame.K_t:
                        ok, info = self.entrenar_modelo()
                        msg = info if ok else f"Error: {info}"
                    if e.key == pygame.K_c:
                        msg = self.exportar_datos_csv()
                    if e.key == pygame.K_f:
                        self._toggle_fullscreen()
                    if e.key == pygame.K_q:
                        self.corriendo = False
                        esperando = False
                        return

    # ----------------- render / loop -----------------
    def _update_frame(self) -> None:
        self.fondo_x1 -= self.fondo_speed
        self.fondo_x2 -= self.fondo_speed

        if self.fondo_x1 <= -self.w:
            self.fondo_x1 = self.w
        if self.fondo_x2 <= -self.w:
            self.fondo_x2 = self.w

        self.pantalla.blit(self.fondo_img, (self.fondo_x1, 0))
        self.pantalla.blit(self.fondo_img, (self.fondo_x2, 0))

        self.frame_count += 1
        if self.frame_count >= self.frame_speed:
            self.current_frame = (self.current_frame + 1) % len(self.jugador_frames)
            self.frame_count = 0

        jugador_sprite = self.jugador_frames[self.current_frame]
        if self.agachado:
            sprite_agachado = pygame.transform.scale(jugador_sprite, self.player_size_agachado)
            self.pantalla.blit(sprite_agachado, (self.jugador.x, self.jugador.y))
        else:
            self.pantalla.blit(jugador_sprite, (self.jugador.x, self.jugador.y))

        self.pantalla.blit(self.nave_img, (self.nave.x, self.nave.y))

        if self.bala_disparada:
            self.bala.x += self.velocidad_bala
            self.frame_bala += 1

        if self.bala.x < -self.bullet_size[0]:
            self.reset_bala()
            if self.modo_auto and self.agachado:
                self.terminar_agacharse()

        self.pantalla.blit(self.bala_img, (self.bala.x, self.bala.y))

        if self.jugador.colliderect(self.bala):
            self._reset_estado_juego()

        # HUD central: bala baja/alta
        if self.bala_disparada:
            if self.altura_bala_relativa == 1.0:
                tipo_txt = "BALA ALTA"
                accion_txt = "AGÁCHATE"
                color_principal = (255, 95, 95)
                color_fondo = (60, 18, 25)
            else:
                tipo_txt = "BALA BAJA"
                accion_txt = "SALTA"
                color_principal = (70, 255, 135)
                color_fondo = (15, 55, 32)

            card_w = int(330 * self.scale)
            card_h = int(80 * self.scale)
            card_x = self.w // 2 - card_w // 2
            card_y = int(16 * self.scale)

            hud = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(hud, (*color_fondo, 210), (0, 0, card_w, card_h), border_radius=18)
            self.pantalla.blit(hud, (card_x, card_y))
            pygame.draw.rect(self.pantalla, color_principal, (card_x, card_y, card_w, card_h), 3, border_radius=18)

            fuente_tipo = pygame.font.SysFont("Arial Black", int(19 * self.scale))
            fuente_accion = pygame.font.SysFont("Arial Black", int(34 * self.scale))
            tipo = fuente_tipo.render(tipo_txt, True, color_principal)
            accion = fuente_accion.render(accion_txt, True, self.BLANCO)
            self.pantalla.blit(tipo, (card_x + card_w // 2 - tipo.get_width() // 2, card_y + int(8 * self.scale)))
            self.pantalla.blit(accion, (card_x + card_w // 2 - accion.get_width() // 2, card_y + int(35 * self.scale)))

        # Estado del jugador: SALTANDO / AGACHADO
        estado_jugador = None
        color_estado = (0, 255, 130)
        color_fondo_estado = (10, 55, 32)

        if self.agachado:
            estado_jugador = "AGACHADO"
            color_estado = (80, 190, 255)
            color_fondo_estado = (15, 35, 55)
        elif self.salto:
            estado_jugador = "SALTANDO"
            color_estado = (0, 255, 130)
            color_fondo_estado = (10, 60, 35)

        if estado_jugador:
            estado_font = pygame.font.SysFont("Arial", int(18 * self.scale), bold=True)
            estado = estado_font.render(estado_jugador, True, self.BLANCO)
            bg_w = estado.get_width() + int(30 * self.scale)
            bg_h = estado.get_height() + int(16 * self.scale)
            bg_x = int(12 * self.scale)
            bg_y = int(14 * self.scale)
            pygame.draw.rect(self.pantalla, color_fondo_estado, (bg_x, bg_y, bg_w, bg_h), border_radius=10)
            pygame.draw.rect(self.pantalla, color_estado, (bg_x, bg_y, bg_w, bg_h), 2, border_radius=10)
            self.pantalla.blit(estado, (bg_x + int(15 * self.scale), bg_y + int(8 * self.scale)))

        if self.modelo_entrenado and self.modo_auto and self.ultima_proba_salto is not None:
            info = f"IA activa  |  Probabilidad de salto: {self.ultima_proba_salto:.2f}"
            txt = self.fuente_chica.render(info, True, self.BLANCO)
            bg_w = txt.get_width() + int(28 * self.scale)
            bg_h = txt.get_height() + int(16 * self.scale)
            bg_x = int(12 * self.scale)
            bg_y = self.h - bg_h - int(12 * self.scale)
            pygame.draw.rect(self.pantalla, (15, 18, 30), (bg_x, bg_y, bg_w, bg_h), border_radius=10)
            pygame.draw.rect(self.pantalla, (255, 215, 80), (bg_x, bg_y, bg_w, bg_h), 2, border_radius=10)
            self.pantalla.blit(txt, (bg_x + int(14 * self.scale), bg_y + int(8 * self.scale)))

    def loop(self) -> None:
        reloj = pygame.time.Clock()
        self.mostrar_menu()

        while self.corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        self.corriendo = False
                    elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                        self._reset_estado_juego()
                        self.mostrar_menu()
                    elif e.key == pygame.K_f:
                        self._toggle_fullscreen()
                    elif e.key == pygame.K_SPACE and not self.modo_auto:
                        # Guardamos el intento de salto aunque el personaje siga en el aire.
                        # Así el auto aprende patrones de saltos repetidos.
                        self.salto_pulsado = True
                        self.iniciar_salto()
                    elif e.key == pygame.K_DOWN and not self.modo_auto:
                        self.iniciar_agacharse()
                elif e.type == pygame.KEYUP:
                    if e.key == pygame.K_DOWN and not self.modo_auto:
                        self.terminar_agacharse()

            if not self.corriendo:
                break

            if self.modo_auto:
                if self._auto_salto_cooldown > 0:
                    self._auto_salto_cooldown -= 1

                accion = self.decision_auto()

                # accion 0 = soltarse / ponerse de pie.
                if accion == 0:
                    if self.agachado:
                        self.terminar_agacharse()

                elif accion == 1:
                    # Salto por evento: puede repetirse si el patrón lo pide,
                    # pero no en frames consecutivos.
                    if self.agachado:
                        self.terminar_agacharse()
                    if self.en_suelo and self._auto_salto_cooldown <= 0:
                        self.iniciar_salto()
                        self._auto_salto_cooldown = 5

                        # Marcamos este evento como realizado para no repetirlo
                        # hasta que llegue otro salto entrenado.
                        if self._auto_salto_evento_actual is not None:
                            self._auto_saltos_hechos.add(self._auto_salto_evento_actual)
                            if self._auto_salto_pendiente_evento == self._auto_salto_evento_actual:
                                self._auto_salto_pendiente_evento = None
                            self._auto_salto_evento_actual = None

                elif accion == 2:
                    # Agacharse/pararse sí puede hacer reboteo por patrón.
                    if self.en_suelo and not self.salto:
                        self.iniciar_agacharse()

                self._ultima_accion_auto = accion
            else:
                self.registrar_decision_manual()

            if self.salto:
                self.manejar_salto()

            if not self.bala_disparada:
                self.disparar_bala()

            self._update_frame()
            pygame.display.flip()
            reloj.tick(45)

        pygame.quit()


def main() -> None:
    Juego().loop()


if __name__ == "__main__":
    main()
