import pygame
import sys
import math
import random
import configuracion as config

# ==============================================================================
# CONFIGURACIÓN INICIAL Y CONSTANTES
# ==============================================================================
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as _error_audio:
    print(f"[main] Aviso: no se pudo inicializar el audio ({_error_audio}). El juego seguirá sin sonido.")

ANCHO, ALTO = 900, 700
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Solsticio - Poderes Elementales")
RELOJ = pygame.time.Clock()
FPS = 60

# Tamaños con los que se escala cada sprite (deben coincidir con los rects
# de colisión que ya usa el juego, para que la textura calce con la caja).
TAMANO_JUGADOR = (33, 50)
TAMANO_ENEMIGO = (30, 40)
TAMANO_MONEDA = (20, 30)
# La puerta puede ser más alta que un tile (se dibuja "parada" sobre el
# tile, alineada por abajo) para que se vea completa. Si prefieres que
# ocupe exactamente un tile, cámbialo a (40, 40).
TAMANO_PUERTA = (40, 64)

# Sprites que NO cambian por nivel: se cargan una sola vez al iniciar.
ANIMACIONES_JUGADOR = config.cargar_animaciones_jugador(TAMANO_JUGADOR)
ANIMACION_MONEDA = config.cargar_animacion_moneda(TAMANO_MONEDA)
ANIMACION_PUERTA = config.cargar_animacion_puerta(TAMANO_PUERTA)

# Sonidos (efectos + referencia para la música de fondo). Si algún archivo
# no existe, su valor queda en None y simplemente no se reproduce nada.
SONIDOS = config.cargar_sonidos_efectos()

# Tamaño de cada tipo de proyectil (debe coincidir con el rect que se crea
# en la clase Proyectil para que la textura calce con la caja de colisión).
TAMANOS_PROYECTILES = {
    "Fuego":   (20, 18),
    "Hielo":   (20, 20),
    "Piedra":  (28, 28),
    "Viento":  (22, 30),
    "Enemigo": (20, 20),
}
ANIMACIONES_PROYECTILES = config.cargar_animaciones_proyectiles(TAMANOS_PROYECTILES)

# Sprites que SÍ cambian por nivel (bloques, fondo, enemigos). Se actualizan
# cada vez que se llama a cargar_nivel().
TEXTURAS_NIVEL_ACTUAL = {"fondo": None, "bloques": {}}
ANIMACIONES_ENEMIGO_ACTUAL = {"normal": [], "congelado": [], "tirador": [], "tirador_congelado": []}

# Colores (RGB)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL_CIELO = (135, 206, 235)
VERDE = (34, 139, 34)
ROJO = (220, 20, 60)
AMARILLO = (255, 215, 0)
CAFE = (139, 69, 19)
GRIS = (105, 105, 105)
MORADO = (138, 43, 226)

# Colores de Proyectiles
C_FUEGO = (255, 69, 0)
C_HIELO = (0, 255, 255)
C_PIEDRA = (169, 169, 169)
C_VIENTO = (240, 255, 255)
C_PROYECTIL_ENEMIGO = (255, 20, 90)  # proyectil disparado por el enemigo Tirador

# Color de las partículas verdes que acompañan al jugador cuando reaparece
# en el punto de inicio tras recibir daño (además de su animación de "dano").
C_PARTICULA_REVIVIR = (60, 230, 110)

# Colores del aura que rodea al jugador según su poder actual (RGB, sin
# transparencia; la transparencia se aplica al dibujarla). "Ninguno" no
# tiene entrada aquí a propósito: sin poder, no hay aura.
AURA_COLORES = {
    "Fuego":  (255, 110, 20),
    "Hielo":  (90, 220, 255),
    "Piedra": (190, 170, 130),
    "Viento": (225, 255, 250),
}

TAMANO_TILE = 40

FUENTE_UI = pygame.font.SysFont("Arial", 18, bold=True)
FUENTE_TITULO = pygame.font.SysFont("Arial", 50, bold=True)

NOMBRES_NIVELES = [
    "1: Mundo del Volcán ",
    "2: Cavernas de Hielo ",
    "3: Bosque de Piedra ",
    "4: Cumbres del Viento ",
    "5: El Desafío Final "
]

# ==============================================================================
# PANTALLA DE INICIO Y SELECCIÓN DE NIVEL (agregado)
# ------------------------------------------------------------------------------
# No modifica nada del juego ya existente: solo agrega dos estados nuevos
# ("MENU" y "SELECCION_NIVEL") que se dibujan y manejan aparte, antes de que
# arranque el estado "JUGANDO" de siempre.
# ==============================================================================
FUENTE_MENU_OPCION = pygame.font.SysFont("Arial", 24, bold=True)
FUENTE_MENU_CHICA = pygame.font.SysFont("Arial", 16)

# Tecla numérica -> índice de nivel (K_1 -> nivel 0, K_2 -> nivel 1, ...)
TECLAS_NUMERICAS_NIVEL = {
    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4,
    pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3, pygame.K_KP5: 4,
}

# Guarda los rectángulos de cada botón dibujado en pantalla (se rellenan al
# dibujar cada menú) para poder detectar tanto el hover como los clicks del
# mouse sobre ellos.
_BOTONES_NIVEL = []
_BOTON_VOLVER_NIVEL = None
_BOTONES_MENU = []
_BOTONES_PAUSA = []
_SLIDER_MUSICA_RECT = None
_SLIDER_EFECTOS_RECT = None
_BOTON_VOLVER_CONFIG = None
particulas_menu = []


def _dibujar_boton(superficie, rect, texto, fuente, hover=False,
                    color_base=(45, 42, 70), color_borde=MORADO,
                    color_texto=BLANCO, color_hover_fondo=(66, 60, 100),
                    color_hover_borde=None):
    """Dibuja un botón con estética "moderna": esquinas redondeadas, sombra
    suave, una barra de acento a la izquierda y un efecto de resalte cuando
    el mouse está encima (hover). Se usa en todos los menús del juego para
    que se vean consistentes y para poder detectar clicks fácilmente."""
    color_hover_borde = color_hover_borde or AMARILLO

    # Sombra (le da algo de profundidad al botón)
    sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 90), sombra.get_rect(), border_radius=14)
    superficie.blit(sombra, (rect.x + 3, rect.y + 5))

    # Cuando el mouse está encima, el botón "se levanta" un poco y brilla
    rect_dibujo = rect.move(0, -3) if hover else rect.copy()
    fondo = color_hover_fondo if hover else color_base
    borde = color_hover_borde if hover else color_borde
    grosor = 3 if hover else 2

    pygame.draw.rect(superficie, fondo, rect_dibujo, border_radius=14)
    pygame.draw.rect(superficie, borde, rect_dibujo, grosor, border_radius=14)

    # Barra de acento a la izquierda (solo visible en hover, look "moderno")
    if hover:
        barra = pygame.Rect(rect_dibujo.left + 6, rect_dibujo.top + 8, 4, rect_dibujo.height - 16)
        pygame.draw.rect(superficie, AMARILLO, barra, border_radius=2)

    texto_render = fuente.render(texto, True, color_texto)
    superficie.blit(texto_render, texto_render.get_rect(center=rect_dibujo.center))

    return rect_dibujo

def _dibujar_menu_inicio(superficie, tiempo_actual):
    global particulas_menu

    # Fondo con degradado
    for y in range(ALTO):
        t = y / ALTO
        r = int(18 * (1 - t) + 35 * t)
        g = int(15 * (1 - t) + 20 * t)
        b = int(35 * (1 - t) + 70 * t)
        pygame.draw.line(superficie, (r, g, b), (0, y), (ANCHO, y))

    # -------------------------
    # Actualizar partículas
    # -------------------------
    for p in particulas_menu[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vida"] -= 1

        if p["vida"] <= 0:
            particulas_menu.remove(p)
            continue

        alpha = int(255 * p["vida"] / 40)
        radio = max(1, p["vida"] // 10)

        s = pygame.Surface((radio * 2 + 2, radio * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(
            s,
            (*p["color"], alpha),
            (radio + 1, radio + 1),
            radio
        )

        superficie.blit(s, (p["x"] - radio, p["y"] - radio))

    # -------------------------
    # Orbes flotantes
    # -------------------------
    for i, (nombre_poder, color) in enumerate(AURA_COLORES.items()):

        offset_x = math.cos(tiempo_actual / 900 + i) * 25
        offset_y = math.sin(tiempo_actual / 600 + i) * 15

        cx = 120 + i * 220 + offset_x
        cy = 120 + offset_y

        # Crear una partícula
        particulas_menu.append({
            "x": cx,
            "y": cy,
            "vx": random.uniform(-0.25, 0.25),
            "vy": random.uniform(-0.6, -0.2),
            "vida": 40,
            "color": color
        })

        # Brillo exterior
        brillo = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(brillo, (*color, 40), (35, 35), 30)
        superficie.blit(brillo, (cx - 35, cy - 35))

        # Orbe principal
        pygame.draw.circle(superficie, color, (int(cx), int(cy)), 18)
        pygame.draw.circle(superficie, BLANCO, (int(cx - 5), int(cy - 5)), 4)

    # -------------------------
    # Título
    # -------------------------
    titulo = FUENTE_TITULO.render("SOLSTICIO", True, AMARILLO)
    subtitulo = FUENTE_TITULO.render("Poderes Elementales", True, BLANCO)

    superficie.blit(
        titulo,
        titulo.get_rect(center=(ANCHO // 2, ALTO // 2 - 90))
    )

    superficie.blit(
        subtitulo,
        subtitulo.get_rect(center=(ANCHO // 2, ALTO // 2 - 40))
    )

    # -------------------------
    # Opciones (botones modernos: hover + clickeables)
    # -------------------------
    global _BOTONES_MENU
    _BOTONES_MENU = []
    mouse_pos = pygame.mouse.get_pos()

    opciones = [
        ("jugar", "Jugar"),
        ("nivel", "Elegir nivel"),
        ("config", "Configuración"),
        ("salir", "Salir"),
    ]

    ancho_boton = 260
    alto_boton = 52
    espacio_boton = 16
    y_boton = ALTO // 2 + 25

    for accion, etiqueta in opciones:
        rect_boton = pygame.Rect(0, 0, ancho_boton, alto_boton)
        rect_boton.center = (ANCHO // 2, y_boton)
        hover = rect_boton.collidepoint(mouse_pos)
        _dibujar_boton(superficie, rect_boton, etiqueta, FUENTE_MENU_OPCION, hover=hover)
        _BOTONES_MENU.append((rect_boton, accion))
        y_boton += alto_boton + espacio_boton

    ayuda = FUENTE_MENU_CHICA.render(
        "Click o ENTER: Jugar   |   L: Elegir nivel   |   ESC: Salir", True, (200, 200, 210)
    )
    superficie.blit(ayuda, ayuda.get_rect(center=(ANCHO // 2, ALTO - 20)))

def _dibujar_seleccion_nivel(superficie):
    global _BOTONES_NIVEL, _BOTON_VOLVER_NIVEL

    # Fondo con degradado (mismo estilo que el menú principal, en vez de un
    # relleno plano, para que se sienta parte del mismo diseño moderno)
    for y_linea in range(ALTO):
        t = y_linea / ALTO
        r = int(20 * (1 - t) + 30 * t)
        g = int(18 * (1 - t) + 16 * t)
        b = int(35 * (1 - t) + 55 * t)
        pygame.draw.line(superficie, (r, g, b), (0, y_linea), (ANCHO, y_linea))

    _BOTONES_NIVEL = []
    mouse_pos = pygame.mouse.get_pos()

    titulo = FUENTE_TITULO.render("Elige un nivel", True, AMARILLO)
    superficie.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 70)))

    alto_boton = 58
    espacio = 14
    total_alto = len(NOMBRES_NIVELES) * alto_boton + (len(NOMBRES_NIVELES) - 1) * espacio
    y = ALTO // 2 - total_alto // 2 + 20

    for i, nombre in enumerate(NOMBRES_NIVELES):
        rect_boton = pygame.Rect(0, 0, 440, alto_boton)
        rect_boton.center = (ANCHO // 2, y)
        hover = rect_boton.collidepoint(mouse_pos)
        _dibujar_boton(superficie, rect_boton, nombre.strip(), FUENTE_MENU_OPCION, hover=hover)

        _BOTONES_NIVEL.append((rect_boton, i))
        y += alto_boton + espacio

    # Botón para volver al menú principal (clickeable, además de ESC)
    rect_volver = pygame.Rect(0, 0, 170, 42)
    rect_volver.center = (ANCHO // 2, ALTO - 55)
    hover_volver = rect_volver.collidepoint(mouse_pos)
    _dibujar_boton(
        superficie, rect_volver, "< Volver", FUENTE_MENU_CHICA, hover=hover_volver,
        color_base=(35, 32, 55), color_borde=GRIS,
    )
    _BOTON_VOLVER_NIVEL = rect_volver

    ayuda = FUENTE_MENU_CHICA.render(
        "Click o teclas 1-5 para elegir  |  ESC para volver", True, (200, 200, 210)
    )
    superficie.blit(ayuda, ayuda.get_rect(center=(ANCHO // 2, ALTO - 15)))


def _iniciar_nivel_desde_menu(indice_nivel):
    """
    Prepara todas las variables para arrancar a jugar el nivel indicado
    desde cero (vidas y monedas reiniciadas), igual que hace la tecla 'R'
    para el nivel 0. Devuelve los valores que main() necesita actualizar.
    """
    poder = obtener_poder_por_nivel(indice_nivel)
    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(indice_nivel)
    return poder, inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel


def _dibujar_pausa(superficie):
    """Dibuja el menú de pausa como un overlay moderno sobre la partida
    (que se sigue viendo "congelada" detrás), con botones para continuar,
    volver al menú principal o salir del juego. Se accede presionando ESC
    mientras se está jugando."""
    global _BOTONES_PAUSA
    _BOTONES_PAUSA = []
    mouse_pos = pygame.mouse.get_pos()

    # Oscurece la partida detrás para resaltar el panel de pausa
    velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    velo.fill((10, 8, 20, 165))
    superficie.blit(velo, (0, 0))

    # Panel central
    ancho_panel, alto_panel = 380, 400
    panel = pygame.Rect(0, 0, ancho_panel, alto_panel)
    panel.center = (ANCHO // 2, ALTO // 2)

    sombra_panel = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(sombra_panel, (0, 0, 0, 110), sombra_panel.get_rect(), border_radius=18)
    superficie.blit(sombra_panel, (panel.x + 4, panel.y + 6))

    pygame.draw.rect(superficie, (32, 28, 52), panel, border_radius=18)
    pygame.draw.rect(superficie, MORADO, panel, 2, border_radius=18)

    titulo = FUENTE_TITULO.render("Pausa", True, AMARILLO)
    titulo_rect = titulo.get_rect(center=(panel.centerx, panel.top + 55))
    superficie.blit(titulo, titulo_rect)

    opciones = [
        ("continuar", "Continuar"),
        ("config", "Configuración"),
        ("menu", "Menú principal"),
        ("salir", "Salir del juego"),
    ]

    ancho_boton, alto_boton, espacio_boton = 260, 50, 14
    y_boton = titulo_rect.bottom + 35

    for accion, etiqueta in opciones:
        rect_boton = pygame.Rect(0, 0, ancho_boton, alto_boton)
        rect_boton.center = (panel.centerx, y_boton)
        hover = rect_boton.collidepoint(mouse_pos)
        _dibujar_boton(superficie, rect_boton, etiqueta, FUENTE_MENU_OPCION, hover=hover)
        _BOTONES_PAUSA.append((rect_boton, accion))
        y_boton += alto_boton + espacio_boton

    ayuda = FUENTE_MENU_CHICA.render("ESC para continuar", True, (200, 200, 210))
    superficie.blit(ayuda, ayuda.get_rect(center=(panel.centerx, panel.bottom - 20)))


def _dibujar_slider(superficie, x, y, ancho, etiqueta, valor, fuente_etiqueta):
    """Dibuja un slider horizontal (valor entre 0.0 y 1.0) con su etiqueta y
    el porcentaje actual arriba. Devuelve el pygame.Rect del "track" (la
    barra), que se usa después para detectar clicks y arrastre del mouse."""
    alto_track = 10
    rect_track = pygame.Rect(x, y, ancho, alto_track)

    etiqueta_render = fuente_etiqueta.render(f"{etiqueta}: {int(valor * 100)}%", True, BLANCO)
    superficie.blit(etiqueta_render, (x, y - 30))

    # Fondo de la barra
    pygame.draw.rect(superficie, (45, 42, 70), rect_track, border_radius=5)

    # Parte "rellena" según el volumen actual
    ancho_relleno = int(ancho * valor)
    if ancho_relleno > 0:
        rect_relleno = pygame.Rect(x, y, ancho_relleno, alto_track)
        pygame.draw.rect(superficie, MORADO, rect_relleno, border_radius=5)

    pygame.draw.rect(superficie, (90, 85, 130), rect_track, 2, border_radius=5)

    # Manija circular
    cx_manija = x + ancho_relleno
    cy_manija = y + alto_track // 2
    pygame.draw.circle(superficie, AMARILLO, (cx_manija, cy_manija), 10)
    pygame.draw.circle(superficie, BLANCO, (cx_manija, cy_manija), 10, 2)

    return rect_track


def _valor_slider_desde_x(rect_track, x_mouse):
    """Convierte la posición X del mouse en un valor entre 0.0 y 1.0 según
    dónde caiga dentro del track del slider (recortado a los bordes)."""
    if rect_track.width <= 0:
        return 0.0
    valor = (x_mouse - rect_track.x) / rect_track.width
    return max(0.0, min(1.0, valor))


def _dibujar_configuracion(superficie, volumen_musica, volumen_efectos):
    """Dibuja el menú de Configuración: sliders de volumen (música y
    efectos), con el mismo estilo moderno del resto de los menús."""
    global _SLIDER_MUSICA_RECT, _SLIDER_EFECTOS_RECT, _BOTON_VOLVER_CONFIG

    # Fondo con degradado, mismo estilo que los demás menús
    for y_linea in range(ALTO):
        t = y_linea / ALTO
        r = int(20 * (1 - t) + 30 * t)
        g = int(18 * (1 - t) + 16 * t)
        b = int(35 * (1 - t) + 55 * t)
        pygame.draw.line(superficie, (r, g, b), (0, y_linea), (ANCHO, y_linea))

    mouse_pos = pygame.mouse.get_pos()

    titulo = FUENTE_TITULO.render("Configuración", True, AMARILLO)
    superficie.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 90)))

    ancho_slider = 380
    x_slider = ANCHO // 2 - ancho_slider // 2

    _SLIDER_MUSICA_RECT = _dibujar_slider(
        superficie, x_slider, 240, ancho_slider, "Música", volumen_musica, FUENTE_MENU_OPCION
    )
    _SLIDER_EFECTOS_RECT = _dibujar_slider(
        superficie, x_slider, 340, ancho_slider, "Efectos de sonido", volumen_efectos, FUENTE_MENU_OPCION
    )

    # Botón volver
    rect_volver = pygame.Rect(0, 0, 200, 46)
    rect_volver.center = (ANCHO // 2, 450)
    hover_volver = rect_volver.collidepoint(mouse_pos)
    _dibujar_boton(
        superficie, rect_volver, "< Volver", FUENTE_MENU_OPCION, hover=hover_volver,
        color_base=(35, 32, 55), color_borde=GRIS,
    )
    _BOTON_VOLVER_CONFIG = rect_volver

    ayuda = FUENTE_MENU_CHICA.render(
        "Arrastra las barras para ajustar el volumen   |   ESC para volver", True, (200, 200, 210)
    )
    superficie.blit(ayuda, ayuda.get_rect(center=(ANCHO // 2, ALTO - 30)))


# ==============================================================================
# DISEÑO DE LOS 5 NIVELES
# ------------------------------------------------------------------------------
# Símbolos usados en el mapa de texto:
#   "T" -> plataforma / suelo          "S" -> pincho (trampa)
#   "C" -> moneda                      "D" -> puerta (fin de nivel)
#   "@" -> punto de inicio del jugador
#   "E" -> enemigo Patrulla (camina y da la vuelta al chocar con una pared)
#   "F" -> enemigo Tirador (dispara proyectiles al jugador y puede saltar
#          obstáculos bajos para perseguirlo)
# Los niveles crecen en longitud y dificultad: más enemigos, más pinchos y
# plataformas más exigentes a medida que se avanza.
# ==============================================================================
NIVELES = [
    # Nivel 1 (Mundo del Volcán) - Introducción: terreno amplio, pocos enemigos, sin poder elemental
    [
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                               C C             D    ",
        "                                                                              TTTTT                 ",
        "                                                  CFC          C C                                  ",
        "                                                 TTTTT    T   TTTTT                                 ",
        "                                                                                                    ",
        "                                        T   TTT                          TTTT                       ",
        "    C  C  C        C        C      C                                                 CFC C          ",
        "  TTTTTTTTTTTT    TTT      TTT    TTT                                               TTTTTTT         ",
        "                                                        C C                                         ",
        "                                                       TTTTTT       TTT                             ",
        "   @                          E                                E   F                                ",
        "TTTTTTTTTTTTTTTTTTTTT   TTTTTTTTTTTTTTTTTSSSSSTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
    ],
    # Nivel 2 (Cavernas de Hielo) - Se desbloquea el poder de Fuego; más plataformas pequeñas y enemigos tiradores
    [
        "                                                                            ",
        "                                                                            ",
        "                                                                            ",
        "                                                                      CCCD  ",
        "                                                                     TTTTTT ",
        "                                       CCC                  T               ",
        "                                      TTTTTT                   CCC          ",
        "                                   T                   CF     TTTTTT        ",
        "                     CCC                              TTTTT                 ",
        "                    TTTTT     CFC            T                              ",
        "                             TTTTT              CCC                         ",
        "                  T                            TTTTTT                       ",
        "             CCC          T                                                 ",
        "            TTTTT                                                           ",
        "        T                                                                   ",
        " @           E           E             E                          E         ",
        "TTTTTTT   TTTTTTT     TTTTTTTTT     TTTTTTTSSSSSSSTTTTTTTTTSSSSSTTTTTTTTTTTT",
    ],
    # Nivel 3 (Bosque de Piedra) - Se desbloquea el poder de Hielo; terreno más vertical y denso en trampas
    [
        "                                                                                      ",
        "                                                                                      ",
        "                                                                                      ",
        "                                                                     CCC              ",
        "                                                       CCC          TTTTT             ",
        "                                         CCCF         TTTTT                           ",
        "                           CCC          TTTTT                                         ",
        "                          TTTTT                              CCCF               TTTTT ",
        "                   CCCF                        CCC          TTTTT                     ",
        "                  TTTTT          CCC          TTTTT                                   ",
        "                                TTTTT                                                 ",
        "         T                                                        T                   ",
        "    CC                  T             E             T                                 ",
        "   TTTT                               T                                    CCC    D   ",
        "            TTTTT                                                         TTTTT       ",
        "  @             E                            E                                E       ",
        "TTTTTTTTT     TTTTTTTSSSSSSSTTTTTTT       TTTTTTTSSSSSSSTTTTTTTSSSSSSSTTTTTTTTTTTTTTTT",
    ],
    # Nivel 4 (Cumbres del Viento) - Se desbloquea el poder de Piedra; plataformas estrechas sobre un mar de pinchos
    [
        "                                                                                              ",
        "                                                                                              ",
        "                                                                              CEC    D        ",
        "                                                      CCC                    TTTTT            ",
        " @CC                                  CFC            TTTTT                                    ",
        "TTTT                  CFC            TTTTT                                                    ",
        "                     TTTTT                         E               T                          ",
        "       CE                                          T                                          ",
        "      TTTT                         T                                  CFC                     ",
        "                   T                                                 TTTTT                    ",
        "                           T                               T                                  ",
        "           T                  CFC          T                                                  ",
        "              CFC            TTTTT                            CFC          T                  ",
        "             TTTTT                            CFC            TTTTT                            ",
        "                                             TTTTT                                            ",
        "                                                                                              ",
        "TTTTTSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSTTTTTTTTTTT",
    ],
    # Nivel 5 (El Desafío Final) - Se desbloquea el poder de Viento; el reto más largo y denso en enemigos
    [
        "                                                                                                              ",
        "                                                                                                              ",
        "                                                                                                   CCC   D    ",
        "                                                                       CFC                        TTTTT       ",
        "                                                 CCCF                 TTTTT                                   ",
        "                                                TTTTT                                CFC                      ",
        "                                T                        CFC                        TTTTT                     ",
        "                                                        TTTTT                                                 ",
        "                        T          CFC                                         CFC                            ",
        "                                  TTTTT                                       TTTTT                           ",
        "        T          CFC                                T          CCCE                                         ",
        "                  TTTTT    CFC                                  TTTTT                                         ",
        "    CC                    TTTTT            CCCE                             T                ECC              ",
        "   TTTT      CFC                          TTTTT                                             TTTTT             ",
        "            TTTTT                                             T                                               ",
        "                                        T                                                                     ",
        " @      E                                                                                 T                   ",
        "TTTTTTTTTTTSSSSSSSSSSSSSSSSSSSSSSSSSSSSS SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSTTTTTT",
    ],
]

# ==============================================================================
# CLASES DEL JUEGO
# ==============================================================================
class Jugador:
    def __init__(self, x, y, animaciones=None):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.vel_y = 0
        self.velocidad = 5
        self.fuerza_salto = -15.5
        self.gravedad = 0.52
        self.velocidad_caida_maxima = 14
        self.en_suelo = False
        self.direccion = 1

        self.ventana_coyote = 90
        self.tiempo_ultimo_en_suelo = 0
        self.corte_salto = -6

        self.animaciones = animaciones or {}
        self.estado = "idle"
        self.tiempo_inicio_estado = pygame.time.get_ticks()

        # --- NUEVO: Control de daño ---
        self.tiempo_herido = 0
        self.duracion_dano = 800  # milisegundos que dura la animación bloqueando el control

    def recibir_dano(self, inicio_x, inicio_y, tiempo_actual, sonido_dano=None):
        """NUEVO: Se llama cuando el jugador recibe daño.
        'sonido_dano' es opcional (un pygame.mixer.Sound ya cargado); si se
        entrega, se reproduce justo en el momento del golpe/reaparición."""
        self.rect.topleft = (inicio_x, inicio_y+1)  # +1 para que no quede justo en el borde del suelo
        self.vel_y = 0
        self.tiempo_herido = tiempo_actual
        self.estado = "dano"
        self.tiempo_inicio_estado = tiempo_actual

        if sonido_dano is not None:
            sonido_dano.play()

    def es_vulnerable(self, tiempo_actual):
        """NUEVO: Retorna True si ya pasó el tiempo de aturdimiento/animación."""
        return tiempo_actual - self.tiempo_herido >= self.duracion_dano

    def mover(self, dx, dy, plataformas):
        # ... (Tu función mover() se queda exactamente igual) ...
        self.rect.x += dx
        for p in plataformas:
            if self.rect.colliderect(p):
                if dx > 0: self.rect.right = p.left
                if dx < 0: self.rect.left = p.right

        self.rect.y += dy
        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if dy > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.en_suelo = True
                if dy < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

    def actualizar(self, plataformas):
        tiempo_actual = pygame.time.get_ticks()
        
        # Revisamos si está en media animación de daño
        esta_herido = not self.es_vulnerable(tiempo_actual)

        self.vel_y += self.gravedad
        if self.vel_y > self.velocidad_caida_maxima:
            self.vel_y = self.velocidad_caida_maxima

        teclas = pygame.key.get_pressed()
        dx = 0
        
        # NUEVO: Solo permitimos que se mueva si NO está herido
        if not esta_herido:
            if teclas[pygame.K_a]: 
                dx = -self.velocidad
                self.direccion = -1
            if teclas[pygame.K_d]: 
                dx = self.velocidad
                self.direccion = 1

            if self.en_suelo:
                self.tiempo_ultimo_en_suelo = tiempo_actual

            salto_presionado = teclas[pygame.K_w] or teclas[pygame.K_SPACE]
            dentro_de_coyote = (tiempo_actual - self.tiempo_ultimo_en_suelo) <= self.ventana_coyote

            if salto_presionado and dentro_de_coyote:
                self.vel_y = self.fuerza_salto
                self.tiempo_ultimo_en_suelo = -999999  
            elif not salto_presionado and self.vel_y < self.corte_salto:
                self.vel_y = self.corte_salto

        self.mover(dx, self.vel_y, plataformas)

        # --- Determinar estado de animación ---
        if esta_herido:
            nuevo_estado = "dano"  # Forzar animación si está herido
        elif not self.en_suelo and self.vel_y < 0:
            nuevo_estado = "saltar"
        elif not self.en_suelo and self.vel_y > 0:
            nuevo_estado = "caer"
        elif dx != 0:
            nuevo_estado = "correr"
        else:
            nuevo_estado = "idle"

        if nuevo_estado != self.estado:
            self.estado = nuevo_estado
            self.tiempo_inicio_estado = tiempo_actual

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)

        frames = self.animaciones.get(self.estado, [])
        sprite = config.obtener_frame_actual(
            frames, self.tiempo_inicio_estado, config.VELOCIDAD_ANIMACION_JUGADOR
        )

        if sprite is not None:
            if self.direccion == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            superficie.blit(sprite, rect_pantalla)
        else:
            # NUEVO: Dibuja un rectángulo ROJO si está herido y aún no tienes el sprite de daño
            color_respaldo = ROJO if self.estado == "dano" else AZUL_CIELO
            pygame.draw.rect(superficie, color_respaldo, rect_pantalla)
            ojo_x = rect_pantalla.x + (20 if self.direccion == 1 else 5)
            pygame.draw.rect(superficie, NEGRO, (ojo_x, rect_pantalla.y + 5, 5, 5))
            pygame.draw.rect(superficie, NEGRO, rect_pantalla, 2)

class Proyectil:
    def __init__(self, x, y, direccion, tipo, animaciones=None):
        self.tipo = tipo
        self.direccion = direccion

        # Frames de animación (configuracion.py). Si viene vacío o None,
        # dibujar() usa el círculo/rectángulo de color de siempre.
        self.animaciones = animaciones or []
        self.tiempo_creacion = pygame.time.get_ticks()

        if tipo == "Fuego":
            self.rect = pygame.Rect(x, y, 12, 12)
            self.velocidad = 7
            self.color = C_FUEGO
            self.dano = 35
        elif tipo == "Hielo":
            self.rect = pygame.Rect(x, y, 10, 10)
            self.velocidad = 6
            self.color = C_HIELO
            self.dano = 20
        elif tipo == "Piedra":
            self.rect = pygame.Rect(x, y, 14, 14)
            self.velocidad = 5
            self.color = C_PIEDRA
            self.dano = 55
        elif tipo == "Viento":
            self.rect = pygame.Rect(x, y, 10, 15)
            self.velocidad = 10
            self.color = C_VIENTO
            self.dano = 15
        elif tipo == "Enemigo":
            # Proyectil disparado por el enemigo Tirador contra el jugador.
            self.rect = pygame.Rect(x, y, 10, 10)
            self.velocidad = 6
            self.color = C_PROYECTIL_ENEMIGO
            self.dano = 0  # el daño al jugador se maneja como pérdida de 1 vida, no de HP

    def actualizar(self):
        self.rect.x += self.velocidad * self.direccion

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)

        # Va dejando a su paso las mismas partículas elementales que el
        # aura del jugador, con el color propio de su elemento.
        radio_spawn = max(self.rect.width, self.rect.height) * 0.35
        if random.random() < 0.7:
            _generar_particula_elemental(
                rect_pantalla.centerx, rect_pantalla.centery, self.color,
                radio_spawn=radio_spawn,
            )

        sprite = config.obtener_frame_actual(
            self.animaciones, self.tiempo_creacion, config.VELOCIDAD_ANIMACION_PROYECTIL
        )

        if sprite is not None:
            if self.direccion == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            superficie.blit(sprite, sprite.get_rect(center=rect_pantalla.center))
        elif self.tipo in ["Fuego", "Hielo", "Enemigo"]:
            pygame.draw.circle(superficie, self.color, rect_pantalla.center, self.rect.width//2)
        else:
            pygame.draw.rect(superficie, self.color, rect_pantalla)

class Enemigo:
    """Enemigo Patrulla: camina de un lado a otro y da la vuelta al chocar
    con una pared. Si 'puede_saltar' es True, en vez de darse siempre la
    vuelta intentará saltar el obstáculo (útil para el enemigo Tirador que
    persigue al jugador y necesita superar plataformas bajas)."""

    def __init__(self, x, y, animaciones=None, puede_saltar=False):
        self.rect = pygame.Rect(x + 5, y + 10, 30, 40)
        self.velocidad_base = 2
        self.direccion = 1
        self.vel_y = 0
        self.en_suelo = False

        # Sistema de Vida
        self.max_hp = 100
        self.hp = 100

        # Estados
        self.tiempo_congelado = 0

        # --- Salto sobre obstáculos ---
        self.puede_saltar = puede_saltar
        self.fuerza_salto_enemigo = -12
        self.tiempo_prox_salto = 0
        self.cooldown_salto = 900  # ms; evita que "rebote" sin fin contra un muro

        # --- Animación / sprites (configuracion.py) ---
        self.animaciones = animaciones or {"normal": [], "congelado": [], "tirador": [], "tirador_congelado": []}

    def _claves_animacion(self):
        """Devuelve (clave_normal, clave_congelado) en el diccionario de
        animaciones. Las subclases (como el Tirador) sobreescriben esto
        para usar su propio set de sprites."""
        return ("normal", "congelado")

    def actualizar(self, plataformas, tiempo_actual=None):
        if tiempo_actual is None:
            tiempo_actual = pygame.time.get_ticks()

        # Gravedad para que no floten
        self.vel_y += 0.5
        if self.vel_y > 10: self.vel_y = 10
        self.rect.y += self.vel_y

        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

        # Ralentización por Hielo
        velocidad_actual = self.velocidad_base
        if tiempo_actual < self.tiempo_congelado:
            velocidad_actual = self.velocidad_base * 0.4 # Muy lento

        # Mover en X
        self.rect.x += velocidad_actual * self.direccion
        bloqueado = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.direccion == 1: self.rect.right = p.left
                else: self.rect.left = p.right
                bloqueado = True

        # --- NUEVO: Comprobar si llegó al borde de una plataforma ---
        en_borde = False
        if self.en_suelo:
            # Creamos un punto de verificación justo delante y debajo del enemigo
            if self.direccion == 1: # Mirando a la derecha
                punto_verificacion = (self.rect.right + 1, self.rect.bottom + 2)
            else: # Mirando a la izquierda
                punto_verificacion = (self.rect.left - 1, self.rect.bottom + 2)
                
            en_borde = True # Asumimos que es el borde hasta demostrar lo contrario
            for p in plataformas:
                if p.collidepoint(punto_verificacion):
                    en_borde = False # Hay plataforma debajo, no es un borde
                    break

        # Toma de decisiones: si hay abismo o una pared
        if en_borde:
            self.direccion *= -1 # Se devuelve para no caer por el abismo
        elif bloqueado:
            if (self.puede_saltar and self.en_suelo
                    and tiempo_actual >= self.tiempo_prox_salto
                    and tiempo_actual >= self.tiempo_congelado):
                # Intenta saltar el obstáculo en vez de darse la vuelta.
                self.vel_y = self.fuerza_salto_enemigo
                self.tiempo_prox_salto = tiempo_actual + self.cooldown_salto
            else:
                self.direccion *= -1 # Dar la vuelta

    def aplicar_empuje(self, direccion_proyectil, plataformas):
        self.rect.x += 40 * direccion_proyectil
        # Evitar atravesar paredes por el empuje
        for p in plataformas:
            if self.rect.colliderect(p):
                if direccion_proyectil == 1: self.rect.right = p.left
                else: self.rect.left = p.right

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)

        esta_congelado = pygame.time.get_ticks() < self.tiempo_congelado
        clave_normal, clave_congelado = self._claves_animacion()
        if esta_congelado:
            frames = self.animaciones.get(clave_congelado, [])
            velocidad_anim = config.VELOCIDAD_ANIMACION_ENEMIGO_CONGELADO
        else:
            frames = self.animaciones.get(clave_normal, [])
            velocidad_anim = config.VELOCIDAD_ANIMACION_ENEMIGO

        # Se usa tiempo_inicio=0 para que la animación corra de forma
        # continua con el reloj global del juego (no hace falta guardar
        # un "inicio" por enemigo).
        sprite = config.obtener_frame_actual(frames, 0, velocidad_anim)

        if sprite is not None:
            if self.direccion == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            superficie.blit(sprite, rect_pantalla)
        else:
            # --- Dibujo de respaldo (sin sprite configurado todavía) ---
            color_enemigo = C_HIELO if esta_congelado else self.color_respaldo()
            pygame.draw.rect(superficie, color_enemigo, rect_pantalla)
            pygame.draw.rect(superficie, NEGRO, rect_pantalla, 2)
        
        # Barra de Vida
        largo_barra = 30 * (self.hp / self.max_hp)
        barra_rect = pygame.Rect(rect_pantalla.x, rect_pantalla.y - 10, largo_barra, 5)
        pygame.draw.rect(superficie, ROJO, (rect_pantalla.x, rect_pantalla.y - 10, 30, 5)) # Fondo rojo
        pygame.draw.rect(superficie, VERDE, barra_rect) # Vida actual verde

    def color_respaldo(self):
        """Color usado cuando no hay sprite configurado todavía."""
        return MORADO


class EnemigoTirador(Enemigo):
    """Enemigo que dispara proyectiles al jugador cuando lo tiene a la
    vista (misma altura aproximada y dentro de su rango) y que puede
    saltar plataformas bajas para perseguirlo mejor."""

    def __init__(self, x, y, animaciones=None):
        super().__init__(x, y, animaciones, puede_saltar=True)
        self.max_hp = 70   # más frágil que el enemigo Patrulla, a cambio de atacar a distancia
        self.hp = 70
        self.rango_disparo = 380
        self.rango_minimo = 20
        self.tolerancia_altura = 45  # cuánto puede diferir en Y y seguir "viendo" al jugador
        self.cooldown_disparo = 1500  # ms entre disparos
        self.ultimo_disparo = 0

    def _claves_animacion(self):
        return ("tirador", "tirador_congelado")

    def color_respaldo(self):
        return (200, 30, 120)  # magenta oscuro, para distinguirlo del Patrulla

    def intentar_disparar(self, jugador, tiempo_actual):
        """Devuelve un Proyectil si el enemigo decide (y puede) disparar
        en este instante, o None si no."""
        if tiempo_actual < self.tiempo_congelado:
            return None  # congelado no puede disparar

        dx = jugador.rect.centerx - self.rect.centerx
        dy = jugador.rect.centery - self.rect.centery

        if abs(dy) > self.tolerancia_altura:
            return None
        distancia = abs(dx)
        if distancia < self.rango_minimo or distancia > self.rango_disparo:
            return None
        if tiempo_actual - self.ultimo_disparo < self.cooldown_disparo:
            return None

        self.direccion = 1 if dx > 0 else -1
        self.ultimo_disparo = tiempo_actual
        return Proyectil(
            self.rect.centerx, self.rect.centery, self.direccion, "Enemigo",
            ANIMACIONES_PROYECTILES.get("Enemigo", [])
        )

def cargar_nivel(indice_nivel):
    global TEXTURAS_NIVEL_ACTUAL, ANIMACIONES_ENEMIGO_ACTUAL

    # --- Cargar texturas específicas de este nivel (configuracion.py) ---
    TEXTURAS_NIVEL_ACTUAL = config.cargar_texturas_nivel(indice_nivel, (TAMANO_TILE, TAMANO_TILE))
    if TEXTURAS_NIVEL_ACTUAL.get("fondo") is not None:
        TEXTURAS_NIVEL_ACTUAL["fondo"] = pygame.transform.scale(TEXTURAS_NIVEL_ACTUAL["fondo"], (ANCHO, ALTO))

    tipo_enemigo = config.obtener_tipo_enemigo_para_nivel(indice_nivel)
    ANIMACIONES_ENEMIGO_ACTUAL = config.cargar_animaciones_enemigo(tipo_enemigo, TAMANO_ENEMIGO)

    mapa = NIVELES[indice_nivel]
    plataformas, pinchos, monedas, enemigos = [], [], [], []
    puerta = None
    inicio_x, inicio_y = 0, 0
    ancho_nivel = len(mapa[0]) * TAMANO_TILE
    alto_nivel = len(mapa) * TAMANO_TILE

    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            x, y = col_idx * TAMANO_TILE, fila_idx * TAMANO_TILE
            if celda == "T": plataformas.append(pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE))
            elif celda == "S": pinchos.append(pygame.Rect(x, y + TAMANO_TILE//2, TAMANO_TILE, TAMANO_TILE//2))
            elif celda == "C": monedas.append(pygame.Rect(x + 10, y + 10, 20, 20))
            elif celda == "E": enemigos.append(Enemigo(x, y, ANIMACIONES_ENEMIGO_ACTUAL))
            elif celda == "F": enemigos.append(EnemigoTirador(x, y, ANIMACIONES_ENEMIGO_ACTUAL))
            elif celda == "D": puerta = pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE)
            elif celda == "@": inicio_x, inicio_y = x, y + (TAMANO_TILE - 30)

    return inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel

def dibujar_corazon(superficie, x, y):
    pygame.draw.circle(superficie, ROJO, (x - 6, y), 6)
    pygame.draw.circle(superficie, ROJO, (x + 6, y), 6)
    pygame.draw.polygon(superficie, ROJO, [(x - 12, y + 2), (x + 12, y + 2), (x, y + 14)])

# Partículas elementales activas en este momento (lista de diccionarios).
# Es estado global porque las partículas deben persistir y moverse de
# un frame a otro. Tanto el aura del jugador como la estela que dejan
# los proyectiles usan esta misma lista y el mismo estilo visual.
_PARTICULAS_ELEMENTALES = []

def _generar_particula_elemental(x, y, color, radio_spawn=0.0):
    """
    Agrega una partícula nueva cerca de (x, y): con una dispersión
    aleatoria de hasta 'radio_spawn' píxeles a su alrededor, del color
    indicado. La usan tanto el aura del jugador como la estela de los
    proyectiles, así que ambas comparten look & feel.
    """
    angulo = random.uniform(0, math.tau)
    dist = random.uniform(0, radio_spawn)
    _PARTICULAS_ELEMENTALES.append({
        "x": x + math.cos(angulo) * dist,
        "y": y + math.sin(angulo) * dist * 0.7,
        "vx": random.uniform(-8, 8),     # deriva horizontal, px/seg
        "vy": random.uniform(-30, -10),  # flota hacia arriba, px/seg
        "vida": 0.0,
        "vida_max": random.uniform(0.8, 1.5),  # segundos de vida
        "radio": random.uniform(0.5, 1),
        "color": color,
    })

def _actualizar_y_dibujar_particulas_elementales(superficie, dt):
    """
    Actualiza posición y edad de todas las partículas activas (tanto las
    del aura como las de la estela de los proyectiles) y las dibuja con
    su resplandor. Se debe llamar una sola vez por frame, ya que también
    se encarga de descartar las partículas que ya terminaron su ciclo de
    vida.
    """
    for p in _PARTICULAS_ELEMENTALES:
        p["vida"] += dt
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt

    # Descartar las que ya cumplieron su ciclo de vida.
    _PARTICULAS_ELEMENTALES[:] = [p for p in _PARTICULAS_ELEMENTALES if p["vida"] < p["vida_max"]]

    # --- Dibujar cada partícula con su propio resplandor ---
    for p in _PARTICULAS_ELEMENTALES:
        progreso = p["vida"] / p["vida_max"]
        # Fade-in rápido al nacer y fade-out el resto de su vida.
        if progreso < 0.15:
            opacidad = progreso / 0.15
        else:
            opacidad = 1 - (progreso - 0.15) / 0.85
        opacidad = max(0.0, min(1.0, opacidad))
        if opacidad <= 0:
            continue
        radio_actual = p["radio"] * (1 - progreso * 0.6)
        radio_actual = max(0.5, radio_actual)
        radio_glow = radio_actual * 2
        tam = max(2, int(radio_glow * 2))
        capa = pygame.Surface((tam, tam), pygame.SRCALPHA)
        centro = (tam // 2, tam // 2)

        # Resplandor difuso: varias capas concéntricas cada vez más chicas
        # y opacas, para dar la sensación de una leve iluminación.
        capas_glow = 5
        for i in range(capas_glow, 0, -1):
            radio = int(radio_glow * i / capas_glow)
            alpha = int(25 * opacidad * (1 - i / (capas_glow + 1)))
            pygame.draw.circle(capa, (*p["color"], alpha), centro, radio)

        # Núcleo brillante de la partícula.
        alpha_nucleo = int(200 * opacidad)
        pygame.draw.circle(capa, (*p["color"], alpha_nucleo), centro, max(1, int(radio_actual)))

        destino = capa.get_rect(center=(int(p["x"]), int(p["y"])))
        superficie.blit(capa, destino, special_flags=pygame.BLEND_RGBA_ADD)

def dibujar_aura(superficie, rect_pantalla, poder, tiempo_actual):
    """
    Dibuja un aura de partículas alrededor del jugador que simboliza su
    poder actual: pequeñas motas de color (distinto por cada elemento)
    que van naciendo cerca del jugador, flotan lentamente hacia arriba
    y se desvanecen, dejando además un leve resplandor a su alrededor.
    Si el poder es "Ninguno" (o cualquier valor sin color asignado en
    AURA_COLORES) no se generan partículas nuevas; las que ya existían
    simplemente terminan su desvanecimiento con normalidad. Esta misma
    función se encarga de actualizar y dibujar TODAS las partículas
    elementales activas (incluidas las que dejan los proyectiles), por
    eso debe seguir llamándose una sola vez por frame.
    """
    color = AURA_COLORES.get(poder)
    dt = RELOJ.get_time() / 1000  # segundos transcurridos desde el frame anterior

    # --- Generar nuevas partículas alrededor del jugador ---
    if color is not None:
        radio_cuerpo = max(rect_pantalla.width, rect_pantalla.height) / 2
        # ~2-3 partículas nuevas por frame -> un flujo continuo pero sutil.
        if random.random() < 0.8:
            _generar_particula_elemental(
                rect_pantalla.centerx, rect_pantalla.centery, color,
                radio_spawn=radio_cuerpo * 0.9,
            )

    _actualizar_y_dibujar_particulas_elementales(superficie, dt)

def _procesar_dano_jugador(jugador, inicio_x, inicio_y, tiempo_actual, vidas):
    """
    Centraliza lo que pasa cada vez que el jugador recibe daño (enemigo,
    proyectil, pincho o caída): resta una vida, reproduce el sonido de daño
    y hace que el jugador reaparezca en el punto de inicio del nivel. Si con
    ese golpe se quedó sin vidas, además reproduce el sonido de muerte.
    Devuelve la cantidad de vidas actualizada.
    """
    vidas -= 1
    jugador.recibir_dano(inicio_x, inicio_y, tiempo_actual, SONIDOS.get("dano"))

    if vidas <= 0:
        sonido_muerte = SONIDOS.get("muerte")
        if sonido_muerte is not None:
            sonido_muerte.play()

    return vidas


def obtener_poder_por_nivel(nivel):
    if nivel == 0: return "Ninguno"
    elif nivel == 1: return "Fuego"
    elif nivel == 2: return "Hielo"
    elif nivel == 3: return "Piedra"
    else: return "Viento"

# ==============================================================================
# BUCLE PRINCIPAL DEL JUEGO
# ==============================================================================
def main():
    vidas = 3
    monedas_totales = 0
    nivel_actual = 0
    estado_juego = "MENU"  # antes era "JUGANDO": ahora el juego arranca en el menú

    # --- Configuración (nuevo): volumen, pantalla completa y estado del ---
    # --- slider que se está arrastrando con el mouse, si hay alguno.    ---
    volumen_musica = config.VOLUMEN_MUSICA_FONDO
    volumen_efectos = config.VOLUMEN_EFECTOS
    arrastrando_slider = None  # None | "musica" | "efectos"
    origen_configuracion = "MENU"  # a qué pantalla volver al salir de Configuración

    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
    jugador = Jugador(inicio_x, inicio_y, ANIMACIONES_JUGADOR)
    poder_actual = obtener_poder_por_nivel(nivel_actual)
    proyectiles = []
    proyectiles_enemigos = []
    ultimo_disparo = 0

    config.reproducir_musica_fondo(volumen_musica)

    corriendo = True
    while corriendo:
        RELOJ.tick(FPS)
        tiempo_actual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                if estado_juego != "JUGANDO":
                    vidas = 3
                    monedas_totales = 0
                    nivel_actual = 0
                    poder_actual = obtener_poder_por_nivel(nivel_actual)
                    estado_juego = "JUGANDO"
                    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    proyectiles.clear()
                    proyectiles_enemigos.clear()

            # --- Pantalla de inicio (agregado): teclado y click funcionan igual ---
            if estado_juego == "MENU":
                accion_menu = None

                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        accion_menu = "jugar"
                    elif evento.key == pygame.K_l:
                        accion_menu = "nivel"
                    elif evento.key == pygame.K_ESCAPE:
                        accion_menu = "salir"

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for rect_boton, accion in _BOTONES_MENU:
                        if rect_boton.collidepoint(evento.pos):
                            accion_menu = accion
                            break

                if accion_menu == "jugar":
                    vidas = 3
                    monedas_totales = 0
                    nivel_actual = 0
                    poder_actual, inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = _iniciar_nivel_desde_menu(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    proyectiles.clear()
                    proyectiles_enemigos.clear()
                    estado_juego = "JUGANDO"
                elif accion_menu == "nivel":
                    estado_juego = "SELECCION_NIVEL"
                elif accion_menu == "config":
                    origen_configuracion = "MENU"
                    estado_juego = "CONFIGURACION"
                elif accion_menu == "salir":
                    corriendo = False

            # --- Pantalla de selección de nivel (agregado): teclado y click ---
            if estado_juego == "SELECCION_NIVEL":
                nivel_elegido = None

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_juego = "MENU"
                    elif evento.key in TECLAS_NUMERICAS_NIVEL:
                        nivel_elegido = TECLAS_NUMERICAS_NIVEL[evento.key]

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if _BOTON_VOLVER_NIVEL is not None and _BOTON_VOLVER_NIVEL.collidepoint(evento.pos):
                        estado_juego = "MENU"
                    else:
                        for rect_boton, indice in _BOTONES_NIVEL:
                            if rect_boton.collidepoint(evento.pos):
                                nivel_elegido = indice
                                break

                if nivel_elegido is not None and nivel_elegido < len(NIVELES):
                    vidas = 3
                    monedas_totales = 0
                    nivel_actual = nivel_elegido
                    poder_actual, inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = _iniciar_nivel_desde_menu(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    proyectiles.clear()
                    proyectiles_enemigos.clear()
                    estado_juego = "JUGANDO"

            # --- Pausa (nuevo): ESC durante la partida abre el menú de pausa ---
            if evento.type == pygame.KEYDOWN and estado_juego == "JUGANDO" and evento.key == pygame.K_ESCAPE:
                estado_juego = "PAUSA"

            elif estado_juego == "PAUSA":
                accion_pausa = None

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        accion_pausa = "continuar"
                    elif evento.key == pygame.K_m:
                        accion_pausa = "menu"

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for rect_boton, accion in _BOTONES_PAUSA:
                        if rect_boton.collidepoint(evento.pos):
                            accion_pausa = accion
                            break

                if accion_pausa == "continuar":
                    estado_juego = "JUGANDO"
                elif accion_pausa == "config":
                    origen_configuracion = "PAUSA"
                    estado_juego = "CONFIGURACION"
                elif accion_pausa == "menu":
                    estado_juego = "MENU"
                elif accion_pausa == "salir":
                    corriendo = False

            # --- Configuración (nuevo): volumen (música/efectos) y pantalla ---
            # --- completa. Se accede desde el menú principal o desde pausa. ---
            elif estado_juego == "CONFIGURACION":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_juego = origen_configuracion

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if _SLIDER_MUSICA_RECT is not None and _SLIDER_MUSICA_RECT.inflate(0, 20).collidepoint(evento.pos):
                        arrastrando_slider = "musica"
                        volumen_musica = _valor_slider_desde_x(_SLIDER_MUSICA_RECT, evento.pos[0])
                        pygame.mixer.music.set_volume(volumen_musica)
                    elif _SLIDER_EFECTOS_RECT is not None and _SLIDER_EFECTOS_RECT.inflate(0, 20).collidepoint(evento.pos):
                        arrastrando_slider = "efectos"
                        volumen_efectos = _valor_slider_desde_x(_SLIDER_EFECTOS_RECT, evento.pos[0])
                        for sonido in SONIDOS.values():
                            if sonido is not None:
                                sonido.set_volume(volumen_efectos)
                    elif _BOTON_VOLVER_CONFIG is not None and _BOTON_VOLVER_CONFIG.collidepoint(evento.pos):
                        estado_juego = origen_configuracion

                elif evento.type == pygame.MOUSEMOTION and arrastrando_slider is not None:
                    if arrastrando_slider == "musica" and _SLIDER_MUSICA_RECT is not None:
                        volumen_musica = _valor_slider_desde_x(_SLIDER_MUSICA_RECT, evento.pos[0])
                        pygame.mixer.music.set_volume(volumen_musica)
                    elif arrastrando_slider == "efectos" and _SLIDER_EFECTOS_RECT is not None:
                        volumen_efectos = _valor_slider_desde_x(_SLIDER_EFECTOS_RECT, evento.pos[0])
                        for sonido in SONIDOS.values():
                            if sonido is not None:
                                sonido.set_volume(volumen_efectos)

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                arrastrando_slider = None

            # --- Volver al menú desde Game Over / Victoria (agregado) ---
            if evento.type == pygame.KEYDOWN and estado_juego in ("GAMEOVER", "VICTORIA"):
                if evento.key == pygame.K_m:
                    estado_juego = "MENU"

        if estado_juego == "JUGANDO":
            # --- DISPARAR ---
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_j] and poder_actual != "Ninguno" and tiempo_actual - ultimo_disparo > 400 and jugador.es_vulnerable(tiempo_actual):
                proyectiles.append(Proyectil(
                    jugador.rect.centerx, jugador.rect.centery, jugador.direccion, poder_actual,
                    ANIMACIONES_PROYECTILES.get(poder_actual, [])
                ))
                ultimo_disparo = tiempo_actual

            jugador.actualizar(plataformas)

            cam_x = max(0, min(jugador.rect.centerx - ANCHO // 2, ancho_nivel - ANCHO))
            cam_y = max(0, min(jugador.rect.centery - ALTO // 2, alto_nivel - ALTO))

            # --- PROYECTILES ---
            for proy in proyectiles[:]:
                proy.actualizar()
                eliminado = False
                
                # Choque con plataformas
                for p in plataformas:
                    if proy.rect.colliderect(p):
                        proyectiles.remove(proy)
                        eliminado = True
                        break
                
                if eliminado: continue

                # Choque con enemigos
                for enemigo in enemigos:
                    if proy.rect.colliderect(enemigo.rect):
                        enemigo.hp -= proy.dano
                        if proy.tipo == "Hielo":
                            enemigo.tiempo_congelado = tiempo_actual + 2000 # 2 segundos
                        elif proy.tipo == "Viento":
                            enemigo.aplicar_empuje(proy.direccion, plataformas)
                        
                        proyectiles.remove(proy)
                        break

            # Limpiar proyectiles fuera de pantalla y enemigos muertos
            proyectiles = [p for p in proyectiles if 0 < p.rect.x < ancho_nivel]
            enemigos = [e for e in enemigos if e.hp > 0]

            # --- COLISIONES CON ENEMIGOS ---
            for enemigo in enemigos:
                enemigo.actualizar(plataformas, tiempo_actual)

                # Los enemigos Tirador intentan dispararle al jugador.
                if isinstance(enemigo, EnemigoTirador):
                    nuevo_proy = enemigo.intentar_disparar(jugador, tiempo_actual)
                    if nuevo_proy is not None:
                        proyectiles_enemigos.append(nuevo_proy)

                # --- COLISIONES CON ENEMIGOS ---
                if jugador.rect.colliderect(enemigo.rect) and jugador.es_vulnerable(tiempo_actual):
                    vidas = _procesar_dano_jugador(jugador, inicio_x, inicio_y, tiempo_actual, vidas)
                    if vidas <= 0: estado_juego = "GAMEOVER"

            # --- PROYECTILES DE LOS ENEMIGOS TIRADOR ---
            for proy in proyectiles_enemigos[:]:
                proy.actualizar()

                # Choque con plataformas
                choco_plataforma = False
                for p in plataformas:
                    if proy.rect.colliderect(p):
                        choco_plataforma = True
                        break
                if choco_plataforma:
                    proyectiles_enemigos.remove(proy)
                    continue

                # Choque con el jugador: resta una vida, igual que un pincho o un enemigo.
                if proy.rect.colliderect(jugador.rect) and jugador.es_vulnerable(tiempo_actual):
                    proyectiles_enemigos.remove(proy)
                    vidas = _procesar_dano_jugador(jugador, inicio_x, inicio_y, tiempo_actual, vidas)
                    if vidas <= 0: estado_juego = "GAMEOVER"

            proyectiles_enemigos = [p for p in proyectiles_enemigos if 0 < p.rect.x < ancho_nivel]

            for pincho in pinchos:
                if jugador.rect.colliderect(pincho) and jugador.es_vulnerable(tiempo_actual):
                    vidas = _procesar_dano_jugador(jugador, inicio_x, inicio_y, tiempo_actual, vidas)
                    if vidas <= 0: estado_juego = "GAMEOVER"

            for moneda in monedas[:]:
                if jugador.rect.colliderect(moneda):
                    monedas.remove(moneda)
                    monedas_totales += 1

                    sonido_moneda = SONIDOS.get("moneda")
                    if sonido_moneda is not None:
                        sonido_moneda.play()

                    if monedas_totales % 10 == 0 and vidas < 3:
                        vidas += 1
                        sonido_vida_extra = SONIDOS.get("vida_extra")
                        if sonido_vida_extra is not None:
                            sonido_vida_extra.play()

            if jugador.rect.colliderect(puerta):
                sonido_puerta = SONIDOS.get("puerta")
                if sonido_puerta is not None:
                    sonido_puerta.play()

                nivel_actual += 1
                if nivel_actual < len(NIVELES):
                    poder_actual = obtener_poder_por_nivel(nivel_actual) # Asignar nuevo poder
                    proyectiles.clear()
                    proyectiles_enemigos.clear()
                    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                else:
                    estado_juego = "VICTORIA"

            if jugador.rect.y > alto_nivel and jugador.es_vulnerable(tiempo_actual):
                vidas = _procesar_dano_jugador(jugador, inicio_x, inicio_y, tiempo_actual, vidas)
                if vidas <= 0: estado_juego = "GAMEOVER"

        # 3. DIBUJADO EN PANTALLA
        # En "PAUSA" se sigue dibujando el mundo del juego (congelado, ya que
        # no se actualiza nada mientras el estado no sea "JUGANDO") para que
        # el menú de pausa aparezca como un overlay sobre la partida.
        fondo_nivel = TEXTURAS_NIVEL_ACTUAL.get("fondo") if estado_juego in ("JUGANDO", "PAUSA") else None
        if fondo_nivel is not None:
            PANTALLA.blit(fondo_nivel, (0, 0))
        else:
            PANTALLA.fill((30, 30, 40))

        if estado_juego in ("JUGANDO", "PAUSA"):
            bloques_nivel = TEXTURAS_NIVEL_ACTUAL.get("bloques", {})
            sprite_plataforma = bloques_nivel.get("T")
            sprite_pincho = bloques_nivel.get("S")
            sprite_moneda = config.obtener_frame_actual(ANIMACION_MONEDA, 0, config.VELOCIDAD_ANIMACION_MONEDA)

            for p in plataformas:
                p_pantalla = p.move(-cam_x, -cam_y)
                if sprite_plataforma is not None:
                    PANTALLA.blit(sprite_plataforma, p_pantalla)
                else:
                    pygame.draw.rect(PANTALLA, VERDE, p_pantalla)
                    pygame.draw.rect(PANTALLA, NEGRO, p_pantalla, 1)

            for p in pinchos:
                p_pantalla = p.move(-cam_x, -cam_y)
                if sprite_pincho is not None:
                    PANTALLA.blit(sprite_pincho, p_pantalla)
                else:
                    pygame.draw.polygon(PANTALLA, GRIS, [(p_pantalla.left, p_pantalla.bottom), (p_pantalla.centerx, p_pantalla.top), (p_pantalla.right, p_pantalla.bottom)])

            for c in monedas:
                c_pantalla = c.move(-cam_x, -cam_y)
                if sprite_moneda is not None:
                    PANTALLA.blit(sprite_moneda, c_pantalla)
                else:
                    pygame.draw.circle(PANTALLA, AMARILLO, c_pantalla.center, 10)
                    pygame.draw.circle(PANTALLA, (218, 165, 32), c_pantalla.center, 10, 2)
            
            for proy in proyectiles: proy.dibujar(PANTALLA, cam_x, cam_y)
            for proy in proyectiles_enemigos: proy.dibujar(PANTALLA, cam_x, cam_y)
            for e in enemigos: e.dibujar(PANTALLA, cam_x, cam_y)

            puerta_pantalla = puerta.move(-cam_x, -cam_y)
            sprite_puerta = config.obtener_frame_actual(ANIMACION_PUERTA, 0, config.VELOCIDAD_ANIMACION_PUERTA)
            if sprite_puerta is not None:
                # Se alinea por abajo con el tile de la puerta, para que
                # sprites más altos que un tile "se paren" sobre él en vez
                # de quedar enterrados o flotando.
                rect_puerta_sprite = sprite_puerta.get_rect(midbottom=puerta_pantalla.midbottom)
                PANTALLA.blit(sprite_puerta, rect_puerta_sprite)
            else:
                pygame.draw.rect(PANTALLA, CAFE, puerta_pantalla)
                pygame.draw.circle(PANTALLA, NEGRO, (puerta_pantalla.right - 10, puerta_pantalla.centery), 4)

            dibujar_aura(PANTALLA, jugador.rect.move(-cam_x, -cam_y), poder_actual, tiempo_actual)

            # Partículas verdes: acompañan a la animación de "dano" mientras
            # el jugador reaparece en el punto de inicio (dura lo mismo que
            # jugador.duracion_dano, el mismo tiempo que dura la invulnerabilidad).
            if tiempo_actual - jugador.tiempo_herido < jugador.duracion_dano:
                rect_jugador_pantalla = jugador.rect.move(-cam_x, -cam_y)
                if random.random() < 0.6:
                    _generar_particula_elemental(
                        rect_jugador_pantalla.centerx, rect_jugador_pantalla.centery,
                        C_PARTICULA_REVIVIR,
                        radio_spawn=max(rect_jugador_pantalla.width, rect_jugador_pantalla.height) * 0.6,
                    )

            jugador.dibujar(PANTALLA, cam_x, cam_y)

            # --- DIBUJAR INTERFAZ (UI) ---
            for i in range(vidas): dibujar_corazon(PANTALLA, 30 + (i * 30), 30)
            
            # Textos
            PANTALLA.blit(FUENTE_UI.render(f"Cristales: {monedas_totales}", True, BLANCO), (20, 50))
            PANTALLA.blit(FUENTE_UI.render(f"Poder: {poder_actual}", True, AMARILLO), (20, 75))
            PANTALLA.blit(FUENTE_UI.render(NOMBRES_NIVELES[nivel_actual], True, BLANCO), (ANCHO - 220, 20))
            PANTALLA.blit(FUENTE_UI.render("Mover: A ↔ D | Saltar: W | Disparar: J | Pausa: ESC", True, BLANCO), (ANCHO//2 - 230, 20))

            # El overlay de pausa se dibuja encima de la partida "congelada"
            if estado_juego == "PAUSA":
                _dibujar_pausa(PANTALLA)

        elif estado_juego == "GAMEOVER":
            PANTALLA.blit(FUENTE_TITULO.render("¡FIN DEL JUEGO!", True, ROJO), (ANCHO//2 - 200, ALTO//2 - 50))
            PANTALLA.blit(FUENTE_UI.render("Presiona 'R' para reiniciar", True, BLANCO), (ANCHO//2 - 120, ALTO//2 + 20))
            PANTALLA.blit(FUENTE_UI.render("Presiona 'M' para volver al menú", True, BLANCO), (ANCHO//2 - 130, ALTO//2 + 50))

        elif estado_juego == "VICTORIA":
            PANTALLA.blit(FUENTE_TITULO.render("¡HAS GANADO!", True, AMARILLO), (ANCHO//2 - 180, ALTO//2 - 50))
            PANTALLA.blit(FUENTE_UI.render(f"Monedas: {monedas_totales} | Presiona 'R' para jugar de nuevo", True, BLANCO), (ANCHO//2 - 200, ALTO//2 + 20))
            PANTALLA.blit(FUENTE_UI.render("Presiona 'M' para volver al menú", True, BLANCO), (ANCHO//2 - 130, ALTO//2 + 50))

        # --- Pantallas nuevas: menú de inicio y selección de nivel (agregado) ---
        elif estado_juego == "MENU":
            _dibujar_menu_inicio(PANTALLA, tiempo_actual)

        elif estado_juego == "SELECCION_NIVEL":
            _dibujar_seleccion_nivel(PANTALLA)

        elif estado_juego == "CONFIGURACION":
            _dibujar_configuracion(PANTALLA, volumen_musica, volumen_efectos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()