import pygame
import sys

pygame.init()

# -------------------------
# Configuración
# -------------------------
ANCHO = 1000
ALTO = 600
FPS = 60

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Plataforma con Cámara")

reloj = pygame.time.Clock()

# -------------------------
# Colores
# -------------------------
AZUL = (135, 206, 235)
VERDE = (40, 180, 40)
ROJO = (220, 60, 60)

# -------------------------
# Mundo
# -------------------------
ANCHO_MUNDO = 3000

# -------------------------
# Jugador
# -------------------------
jugador = pygame.Rect(100, 100, 50, 70)

velocidad_x = 6
velocidad_y = 0

GRAVEDAD = 0.6
SALTO = -13

en_el_suelo = False

# -------------------------
# Cámara
# -------------------------
camera_x = 0

# -------------------------
# Plataformas
# -------------------------
plataformas = [
    pygame.Rect(0, 550, 3000, 50),

    pygame.Rect(300, 450, 180, 20),
    pygame.Rect(650, 370, 180, 20),
    pygame.Rect(1000, 300, 180, 20),
    pygame.Rect(1400, 450, 180, 20),
    pygame.Rect(1800, 350, 180, 20),
    pygame.Rect(2200, 250, 180, 20),
    pygame.Rect(2600, 420, 180, 20),
]

# -------------------------
# Game Loop
# -------------------------
ejecutando = True

while ejecutando:

    reloj.tick(FPS)

    # -------------------------
    # Eventos
    # -------------------------
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_SPACE and en_el_suelo:
                velocidad_y = SALTO
                en_el_suelo = False

    # -------------------------
    # Movimiento Horizontal
    # -------------------------
    teclas = pygame.key.get_pressed()

    dx = 0

    if teclas[pygame.K_LEFT]:
        dx = -velocidad_x

    if teclas[pygame.K_RIGHT]:
        dx = velocidad_x

    jugador.x += dx

    # Colisiones horizontales
    for plataforma in plataformas:

        if jugador.colliderect(plataforma):

            if dx > 0:
                jugador.right = plataforma.left

            elif dx < 0:
                jugador.left = plataforma.right

    # -------------------------
    # Gravedad
    # -------------------------
    velocidad_y += GRAVEDAD
    jugador.y += velocidad_y

    en_el_suelo = False

    # -------------------------
    # Colisiones Verticales
    # -------------------------
    for plataforma in plataformas:

        if jugador.colliderect(plataforma):

            if velocidad_y > 0:

                jugador.bottom = plataforma.top
                velocidad_y = 0
                en_el_suelo = True

            elif velocidad_y < 0:

                jugador.top = plataforma.bottom
                velocidad_y = 0

    # -------------------------
    # Cámara
    # -------------------------
    camera_x = jugador.centerx - ANCHO // 2

    # Limitar la cámara
    if camera_x < 0:
        camera_x = 0

    if camera_x > ANCHO_MUNDO - ANCHO:
        camera_x = ANCHO_MUNDO - ANCHO

    # -------------------------
    # Dibujar
    # -------------------------
    pantalla.fill(AZUL)

    # Dibujar plataformas
    for plataforma in plataformas:

        pygame.draw.rect(
            pantalla,
            VERDE,
            (
                plataforma.x - camera_x,
                plataforma.y,
                plataforma.width,
                plataforma.height
            )
        )

    # Dibujar jugador
    pygame.draw.rect(
        pantalla,
        ROJO,
        (
            jugador.x - camera_x,
            jugador.y,
            jugador.width,
            jugador.height
        )
    )

    pygame.display.flip()

pygame.quit()
sys.exit()