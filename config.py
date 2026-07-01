"""
config.py
---------
Constantes globales del juego "Solsticio: El Ultimo Guardian".
Segun el GDD (seccion 2.4), las constantes van en MAYUSCULAS en este archivo.
"""

import os

import pygame

# Carpeta donde esta este archivo (la raiz del proyecto). Se usa para que las
# rutas de assets funcionen sin importar desde donde ejecutes "python main.py".
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.display.init()
# ----- Ventana -----
ANCHO = 1500
ALTO = 800
FPS = 60
TITULO = "Solsticio: El Ultimo Guardian"

# ----- Controles de Kael -----
# Cambia aqui las teclas sin tocar el resto del codigo.
# Lista completa de codigos de tecla disponibles (pygame.K_...):
# https://www.pygame.org/docs/ref/key.html
TECLA_IZQUIERDA = pygame.K_a
TECLA_DERECHA = pygame.K_d
TECLA_SALTAR = pygame.K_w

# ----- Fisica -----
GRAVEDAD = 0.8
VELOCIDAD_MOVIMIENTO = 5
FUERZA_SALTO = -17

# ----- Suelo -----
ALTURA_SUELO = 80  # alto en pixeles de la franja de suelo, medida desde abajo

# ----- Rutas de assets -----
# Coloca aqui las rutas de tus imagenes, RELATIVAS A LA CARPETA DEL PROYECTO
# (la misma carpeta donde esta este config.py), usando "/" como separador
# aunque estes en Windows. Pueden ser .png, .jpg o .bmp.
# Si una ruta queda vacia o el archivo no existe, se usara un rectangulo
# de color como placeholder para que el juego siga corriendo mientras
# consigues el arte definitivo.

RUTA_FONDO = "assets/fondos/fondo.jpeg"
RUTA_SUELO = "assets/suelo/suelo.png"
RUTA_SPRITE_KAEL = "assets/personajes/kael.png"  # se usa solo si no hay frames de animacion
RUTA_PLATAFORMA = "assets/plataformas/plataforma.png"  # Ej: "assets/plataformas/roca_volcan.png". Si esta vacia, se usa un color solido.

# ----- Animacion de Kael -----
# Carpeta donde estan los frames de cada animacion, nombrados como:
#   kael_idle_0.png, kael_idle_1.png, ...
#   kael_correr_0.png, kael_correr_1.png, ...
#   kael_saltar_0.png, kael_saltar_1.png, ...
# Si para un estado no existe ningun frame, se usa RUTA_SPRITE_KAEL (o el
# placeholder de color) como imagen fija para ese estado.
CARPETA_ANIMACIONES_KAEL = "assets/personajes"
ANIMACION_FPS = 8  # cuantos frames de animacion se muestran por segundo
