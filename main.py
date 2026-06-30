"""
main.py
-------
Punto de entrada del juego. Por ahora solo monta:
- la ventana,
- el fondo,
- el suelo,
- a Kael (con movimiento horizontal y salto).

Esto corresponde al hito de la semana 11 del cronograma del GDD:
"Demo: Kael que se mueve, salta y dispara" (el disparo se agregara despues).
"""

import sys
import os

import pygame

import config
from entidades import Kael


def cargar_fondo():
    """Carga la imagen de fondo o genera un color solido como placeholder."""
    if config.RUTA_FONDO:
        ruta_absoluta = os.path.join(config.BASE_DIR, config.RUTA_FONDO)
        try:
            fondo = pygame.image.load(ruta_absoluta).convert()
            return pygame.transform.scale(fondo, (config.ANCHO, config.ALTO))
        except (pygame.error, FileNotFoundError) as error:
            print(f"[Aviso] No se pudo cargar el fondo '{ruta_absoluta}': {error}. Se usara un color solido.")

    superficie = pygame.Surface((config.ANCHO, config.ALTO))
    superficie.fill((30, 30, 60))  # azul oscuro, color de cielo nocturno provisional
    return superficie


def cargar_suelo():
    """Carga la textura del suelo (en mosaico) o genera un color solido como placeholder."""
    alto_suelo = config.ALTURA_SUELO
    y_suelo = config.ALTO - alto_suelo

    if config.RUTA_SUELO:
        ruta_absoluta = os.path.join(config.BASE_DIR, config.RUTA_SUELO)
        try:
            textura = pygame.image.load(ruta_absoluta).convert_alpha()
            return textura, y_suelo
        except (pygame.error, FileNotFoundError) as error:
            print(f"[Aviso] No se pudo cargar el suelo '{ruta_absoluta}': {error}. Se usara un color solido.")

    superficie = pygame.Surface((config.ANCHO, alto_suelo))
    superficie.fill((80, 50, 30))  # marron tierra, color provisional
    return superficie, y_suelo


def dibujar_suelo(pantalla, textura_suelo, y_suelo):
    """Dibuja la textura del suelo repetida (en mosaico) a lo largo del ancho de la ventana."""
    ancho_textura = textura_suelo.get_width()
    x = 0
    while x < config.ANCHO:
        pantalla.blit(textura_suelo, (x, y_suelo))
        x += ancho_textura


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption(config.TITULO)
    reloj = pygame.time.Clock()

    fondo = cargar_fondo()
    textura_suelo, y_suelo = cargar_suelo()

    # Kael arranca parado justo encima del suelo
    kael = Kael(x=config.ANCHO // 2, y=y_suelo - Kael.ALTO_KAEL)

    ejecutando = True
    while ejecutando:
        # ---- Eventos ----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        # ---- Entrada de teclado ----
        teclas = pygame.key.get_pressed()
        kael.manejar_entrada(teclas)

        # ---- Actualizacion ----
        kael.actualizar(suelo_y=y_suelo)

        # ---- Dibujado ----
        pantalla.blit(fondo, (0, 0))
        dibujar_suelo(pantalla, textura_suelo, y_suelo)
        kael.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(config.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
