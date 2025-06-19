import pygame
import sys
import random

pygame.init()

# ------------ Configuración inicial ------------
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Beyond the Edge")

# Imágenes
fondo       = pygame.image.load("fondo.jpg")
jugador_img = pygame.image.load("jugador.png")
jugador_img = pygame.transform.scale(jugador_img, (64, 64))

TAM_BALA = 150
bala_img = pygame.image.load("bala2.png")
bala_img = pygame.transform.scale(bala_img, (TAM_BALA, TAM_BALA))

casa_img = pygame.image.load("casa2.png")
casa_img = pygame.transform.scale(casa_img, (100, 100))

boss_img = pygame.image.load("boss.png")
boss_img = pygame.transform.scale(boss_img, (60, 60))

TAM_MINERAL = 150
mineral_img = pygame.image.load("minerales4.png")
mineral_img = pygame.transform.scale(mineral_img, (TAM_MINERAL, TAM_MINERAL))

nave_img = pygame.image.load("nave.png")
nave_img = pygame.transform.scale(nave_img, (100, 100))

# ------------ Jugador ------------
jugador_x, jugador_y = 100, 100
vel_jugador = 5
vida = 3

# ------------ Recursos ------------
minerales = []
for _ in range(5):
    x = random.randint(0, ANCHO - TAM_MINERAL)
    y = random.randint(0, ALTO - TAM_MINERAL)
    minerales.append(pygame.Rect(x, y, TAM_MINERAL, TAM_MINERAL))

recolectados = 0
font = pygame.font.Font(None, 36)

# ------------ Base / Casa ------------
base_construida = False
zona_base = pygame.Rect(600, 400, 100, 100)

# ------------ Nave (reemplaza misión) ------------
nave = pygame.Rect(200, 400, 100, 100)
nave_activada = False

# ------------ Enemigo simple ------------
enemigo = pygame.Rect(400, 300, 40, 40)
enemigo_dir = 1

# ------------ Boss ------------
boss = pygame.Rect(600, 100, 60, 60)
boss_vida = 10
vel_boss = 2
cooldown_boss = 1000
ultimo_ataque_boss = 0

# ------------ Balas ------------
balas = []
vel_bala = 10

# ------------ Reloj ------------
reloj = pygame.time.Clock()
corriendo = True

while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            bala_rect = pygame.Rect(
                jugador_x + jugador_img.get_width(),
                jugador_y + jugador_img.get_height() // 2 - TAM_BALA // 2,
                TAM_BALA, TAM_BALA)
            balas.append({"rect": bala_rect, "img": bala_img})

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jugador_x > 0:
        jugador_x -= vel_jugador
    if teclas[pygame.K_RIGHT] and jugador_x < ANCHO - jugador_img.get_width():
        jugador_x += vel_jugador
    if teclas[pygame.K_UP] and jugador_y > 0:
        jugador_y -= vel_jugador
    if teclas[pygame.K_DOWN] and jugador_y < ALTO - jugador_img.get_height():
        jugador_y += vel_jugador

    jugador_rect = pygame.Rect(jugador_x, jugador_y, 64, 64)

    enemigo.x += enemigo_dir * 2
    if enemigo.x <= 0 or enemigo.x >= ANCHO - enemigo.width:
        enemigo_dir *= -1

    # Movimiento Boss
    if base_construida:
        if not boss.colliderect(zona_base):
            boss.x += vel_boss if boss.x < jugador_x else -vel_boss
            boss.y += vel_boss if boss.y < jugador_y else -vel_boss
    else:
        boss.x += vel_boss if boss.x < jugador_x else -vel_boss
        boss.y += vel_boss if boss.y < jugador_y else -vel_boss

    pantalla.blit(fondo, (0, 0))
    pantalla.blit(jugador_img, (jugador_x, jugador_y))

    # Dibujar minerales
    for mineral in minerales[:]:
        pantalla.blit(mineral_img, mineral.topleft)
        if jugador_rect.colliderect(mineral):
            minerales.remove(mineral)
            recolectados += 1

    # Dibujar zona base
    if not base_construida:
        pygame.draw.rect(pantalla, (200, 100, 100), zona_base)
        if jugador_rect.colliderect(zona_base) and recolectados >= 5:
            base_construida = True
            recolectados -= 5
    else:
        pantalla.blit(casa_img, zona_base.topleft)
        texto_base = font.render("Casa construida", True, (255, 255, 0))
        pantalla.blit(texto_base, (zona_base.x - 20, zona_base.y - 30))

    # Dibujar nave
    pantalla.blit(nave_img, nave.topleft)
    if jugador_rect.colliderect(nave) and not nave_activada:
        nave_activada = True
        vida += 3

    texto_nave = font.render(
        "¡Nave activada!" if nave_activada else "Acércate a la nave",
        True, (0, 255, 255) if nave_activada else (255, 255, 255))
    pantalla.blit(texto_nave, (10, 90))

    # Enemigo simple
    pygame.draw.rect(pantalla, (255, 0, 0), enemigo)
    if jugador_rect.colliderect(enemigo):
        vida -= 1
        jugador_x, jugador_y = 100, 100
        pygame.time.delay(500)

    # Boss
    pantalla.blit(boss_img, boss.topleft)
    ahora = pygame.time.get_ticks()
    if (not (base_construida and jugador_rect.colliderect(zona_base))) and jugador_rect.colliderect(boss):
        if ahora - ultimo_ataque_boss > cooldown_boss:
            vida -= 1
            ultimo_ataque_boss = ahora
            jugador_x, jugador_y = 100, 100

    # Balas
    for bala in balas[:]:
        bala["rect"].x += vel_bala
        pantalla.blit(bala["img"], bala["rect"].topleft)
        if bala["rect"].colliderect(boss) and boss_vida > 0:
            boss_vida -= 1
            balas.remove(bala)
        elif bala["rect"].x > ANCHO:
            balas.remove(bala)

    # HUD
    pantalla.blit(font.render(f"Boss HP: {boss_vida}", True, (255, 255, 0)), (boss.x - 10, boss.y - 30))
    pantalla.blit(font.render(f"Recursos: {recolectados}", True, (255, 255, 255)), (10, 10))
    pantalla.blit(font.render(f"Vida: {vida}", True, (255, 0, 0)), (10, 50))

    # Fin del juego
    if vida <= 0:
        pantalla.blit(font.render("¡Has perdido!", True, (255, 0, 0)), (ANCHO // 2 - 100, ALTO // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        break

    if boss_vida <= 0:
        pantalla.fill((0, 0, 0))
        pantalla.blit(font.render("¡Has ganado! Juego completado.", True, (0, 255, 0)), (ANCHO // 2 - 200, ALTO // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        break

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()
