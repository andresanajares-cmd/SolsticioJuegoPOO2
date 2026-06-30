"""
entidades.py
------------
Jerarquia de clases del juego, segun la Fase 2 del GDD (seccion 2.2 y 2.3).

EntidadJuego es la clase abstracta base (Unidad 1 - DRY + abstraccion).
Todas las entidades del juego (Kael, enemigos, proyectiles, cristales,
plataformas...) compartiran esta base en el futuro.

Por ahora se implementa:
- EntidadJuego (abstracta)
- Kael (jugador), con movimiento horizontal, salto y animacion por estados
  (idle / correr / saltar) usando secuencias de imagenes (un archivo por frame).
"""

from abc import ABC, abstractmethod
import os

import pygame

import config


class EntidadJuego(ABC):
    """
    Clase abstracta base de la que heredaran todas las entidades del juego
    (Kael, Enemigo, Proyectil, Cristal, Plataforma, etc).

    Centraliza lo que todas las entidades tienen en comun:
    - posicion (x, y)
    - imagen / rectangulo de colision
    - un id unico generado mediante una variable estatica (_contador_id)
    """

    _contador_id = 0  # variable estatica: cuenta cuantas entidades se han creado

    def __init__(self, x: float, y: float, ancho: int, alto: int, ruta_imagen: str = "", color_placeholder=(255, 0, 255)):
        EntidadJuego._contador_id += 1
        self.id = EntidadJuego._contador_id

        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        self.imagen = self.cargar_imagen(ruta_imagen, ancho, alto, color_placeholder)
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))

    @staticmethod
    def cargar_imagen(ruta_imagen: str, ancho: int, alto: int, color_placeholder):
        """
        Intenta cargar una imagen desde disco. Si la ruta esta vacia o el
        archivo no existe/no se puede leer, genera un rectangulo de color
        solido como placeholder para que el juego no se rompa mientras
        se consiguen los sprites definitivos.
        """
        if ruta_imagen:
            ruta_absoluta = os.path.join(config.BASE_DIR, ruta_imagen)
            try:
                imagen = pygame.image.load(ruta_absoluta).convert_alpha()
                return pygame.transform.scale(imagen, (ancho, alto))
            except (pygame.error, FileNotFoundError) as error:
                print(f"[Aviso] No se pudo cargar la imagen '{ruta_absoluta}': {error}. Se usara un placeholder.")

        superficie = pygame.Surface((ancho, alto))
        superficie.fill(color_placeholder)
        return superficie

    @abstractmethod
    def actualizar(self, *args, **kwargs):
        """Logica de actualizacion por frame. Cada subclase la redefine."""
        raise NotImplementedError

    def dibujar(self, pantalla: pygame.Surface):
        """Dibuja la entidad en pantalla. Las subclases pueden redefinirla si lo necesitan."""
        pantalla.blit(self.imagen, self.rect)


class Kael(EntidadJuego):
    """
    Personaje principal jugable.

    Controles (segun el GDD):
    - Flechas izquierda/derecha: moverse horizontalmente.
    - Espacio: saltar.

    Animacion:
    Tiene tres estados de animacion: "idle" (quieto), "correr" y "saltar".
    Cada estado es una lista de imagenes (frames) cargadas desde archivos
    nombrados "kael_<estado>_<indice>.png" dentro de
    config.CARPETA_ANIMACIONES_KAEL, por ejemplo:
        assets/personajes/kael_idle_0.png
        assets/personajes/kael_idle_1.png
        assets/personajes/kael_correr_0.png
        assets/personajes/kael_correr_1.png
        assets/personajes/kael_saltar_0.png
    Si un estado no tiene frames, se usa RUTA_SPRITE_KAEL como imagen fija.
    """

    ANCHO_KAEL = 40
    ALTO_KAEL = 56

    ESTADOS_ANIMACION = ("idle", "correr", "saltar")

    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            ancho=self.ANCHO_KAEL,
            alto=self.ALTO_KAEL,
            ruta_imagen=config.RUTA_SPRITE_KAEL,
            color_placeholder=(255, 140, 0),  # naranja, mientras no haya sprite
        )

        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_suelo = False
        self.vidas = 3  # segun el GDD, Kael tiene 3 vidas
        self.mirando_derecha = True

        # ---- Animacion ----
        self.animaciones = {
            estado: self._cargar_animacion(estado)
            for estado in self.ESTADOS_ANIMACION
        }
        self.estado_animacion = "idle"
        self.frame_actual = 0
        self.tiempo_acumulado_ms = 0
        self.imagen = self.animaciones[self.estado_animacion][self.frame_actual]

    def _cargar_animacion(self, estado: str):
        """
        Carga la secuencia de frames "kael_<estado>_0.png", "kael_<estado>_1.png", ...
        Se detiene en el primer indice que no encuentre. Si no encuentra
        ningun frame para el estado, usa la imagen fija de Kael (self.imagen,
        ya cargada por EntidadJuego) como unico frame.
        """
        frames = []
        indice = 0
        while True:
            nombre_archivo = f"kael_{estado}_{indice}.png"
            ruta_relativa = os.path.join(config.CARPETA_ANIMACIONES_KAEL, nombre_archivo)
            ruta_absoluta = os.path.join(config.BASE_DIR, ruta_relativa)

            if not os.path.isfile(ruta_absoluta):
                break

            try:
                imagen = pygame.image.load(ruta_absoluta).convert_alpha()
                frames.append(pygame.transform.scale(imagen, (self.ancho, self.alto)))
            except pygame.error as error:
                print(f"[Aviso] No se pudo cargar el frame '{ruta_absoluta}': {error}.")
                break

            indice += 1

        if not frames:
            # No hay frames para este estado: se usa la imagen fija de Kael.
            frames = [self.imagen]

        return frames

    def manejar_entrada(self, teclas):
        """Lee el estado del teclado y define la velocidad horizontal, el salto y la orientacion."""
        self.velocidad_x = 0

        if teclas[pygame.K_LEFT]:
            self.velocidad_x = -config.VELOCIDAD_MOVIMIENTO
            self.mirando_derecha = False
        if teclas[pygame.K_RIGHT]:
            self.velocidad_x = config.VELOCIDAD_MOVIMIENTO
            self.mirando_derecha = True

        if teclas[pygame.K_SPACE] and self.en_suelo:
            self.velocidad_y = config.FUERZA_SALTO
            self.en_suelo = False

    def aplicar_gravedad(self):
        self.velocidad_y += config.GRAVEDAD

    def actualizar(self, suelo_y: int, dt_ms: int = 16):
        """
        Mueve a Kael segun su velocidad actual, aplica gravedad, resuelve
        la colision simple con el suelo y avanza la animacion.
        `suelo_y` es la coordenada Y de la superficie del suelo.
        `dt_ms` son los milisegundos transcurridos desde el frame anterior.
        """
        self.aplicar_gravedad()

        self.x += self.velocidad_x
        self.y += self.velocidad_y

        # Limites laterales de la ventana
        self.x = max(0, min(self.x, config.ANCHO - self.ancho))

        # Colision simple con el suelo
        if self.y + self.alto >= suelo_y:
            self.y = suelo_y - self.alto
            self.velocidad_y = 0
            self.en_suelo = True
        else:
            self.en_suelo = False

        self.rect.topleft = (self.x, self.y)

        self._actualizar_animacion(dt_ms)

    def _actualizar_animacion(self, dt_ms: int):
        """Decide el estado de animacion segun el movimiento y avanza el frame con el tiempo."""
        if not self.en_suelo:
            nuevo_estado = "saltar"
        elif self.velocidad_x != 0:
            nuevo_estado = "correr"
        else:
            nuevo_estado = "idle"

        if nuevo_estado != self.estado_animacion:
            self.estado_animacion = nuevo_estado
            self.frame_actual = 0
            self.tiempo_acumulado_ms = 0

        frames = self.animaciones[self.estado_animacion]
        duracion_frame_ms = 1000 / config.ANIMACION_FPS

        self.tiempo_acumulado_ms += dt_ms
        if self.tiempo_acumulado_ms >= duracion_frame_ms:
            self.tiempo_acumulado_ms = 0
            self.frame_actual = (self.frame_actual + 1) % len(frames)

        frame = frames[self.frame_actual]
        self.imagen = frame if self.mirando_derecha else pygame.transform.flip(frame, True, False)
