"""
config.py
---------
Constantes globales del juego "Solsticio: El Ultimo Guardian".
Segun el GDD (seccion 2.4), las constantes van en MAYUSCULAS en este archivo.
"""

import os

# Carpeta donde esta este archivo (la raiz del proyecto). Se usa para que las
# rutas de assets funcionen sin importar desde donde ejecutes "python main.py".
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----- Ventana -----
ANCHO = 800
ALTO = 600
FPS = 60
TITULO = "Solsticio: El Ultimo Guardian"

# ----- Fisica -----
GRAVEDAD = 0.8
VELOCIDAD_MOVIMIENTO = 5
FUERZA_SALTO = -15

# ----- Suelo -----
ALTURA_SUELO = 80  # alto en pixeles de la franja de suelo, medida desde abajo

# ----- Rutas de assets -----
# Coloca aqui las rutas de tus imagenes, RELATIVAS A LA CARPETA DEL PROYECTO
# (la misma carpeta donde esta este config.py), usando "/" como separador
# aunque estes en Windows. Pueden ser .png, .jpg o .bmp.
# Si una ruta queda vacia o el archivo no existe, se usara un rectangulo
# de color como placeholder para que el juego siga corriendo mientras
# consigues el arte definitivo.

RUTA_FONDO = "assets/fondos/fondo1.jpeg"
RUTA_SUELO = "assets/suelo/suelo.jpeg"
RUTA_SPRITE_KAEL = "assets/personajes/kael.png"
