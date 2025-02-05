import pygame
import math
import sys

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CENTER = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
HEX_RADIUS = 200
BALL_RADIUS = 10
GRAVITY = 0.5
AIR_FRICTION = 0.99
RESTITUTION = 0.8
FRICTION = 0.9
ROTATION_SPEED = 1  # Graus por frame
BALL_COLOR = (255, 0, 0)
HEX_COLOR = (0, 0, 255)
BACKGROUND_COLOR = (255, 255, 255)

class Bola:
    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def atualizar(self):
        self.vy += GRAVITY
        self.vx *= AIR_FRICTION
        self.vy *= AIR_FRICTION
        self.x += self.vx
        self.y += self.vy

    def desenhar(self, tela):
        pygame.draw.circle(tela, BALL_COLOR, (int(self.x), int(self.y)), BALL_RADIUS)

def obter_vertices_hexagono(theta):
    vertices = []
    for i in range(6):
        angulo = math.radians(theta + 60 * i)
        x = CENTER[0] + HEX_RADIUS * math.cos(angulo)
        y = CENTER[1] + HEX_RADIUS * math.sin(angulo)
        vertices.append((x, y))
    return vertices

def obter_normal_aresta(theta, i):
    angulo = math.radians(theta + 30 + 60 * i)
    return (math.cos(angulo), math.sin(angulo))

# Inicialização do Pygame
pygame.init()
tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bola Quicando em Hexágono Giratório")
relogio = pygame.time.Clock()

theta = 0
bola = Bola(CENTER[0], CENTER[1] - HEX_RADIUS + 50)  # Posição inicial

executando = True
while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

    # Atualizar rotação do hexágono
    theta += ROTATION_SPEED
    theta %= 360

    # Obter geometria atual do hexágono
    vertices = obter_vertices_hexagono(theta)
    normais = [obter_normal_aresta(theta, i) for i in range(6)]

    # Atualizar física da bola
    bola.atualizar()

    # Verificar colisões com cada aresta
    for i in range(6):
        A = vertices[i]
        B = vertices[(i+1)%6]
        normal_x, normal_y = normais[i]

        # Cálculo do ponto mais próximo na aresta
        ax, ay = A
        bx, by = B
        abx, aby = bx - ax, by - ay
        apx, apy = bola.x - ax, bola.y - ay
        t = (apx * abx + apy * aby) / (abx**2 + aby**2 + 1e-8)  # Evita divisão por zero

        if t < 0:
            px, py = ax, ay
        elif t > 1:
            px, py = bx, by
        else:
            px, py = ax + t * abx, ay + t * aby

        # Verificar colisão
        dx, dy = bola.x - px, bola.y - py
        distancia_quad = dx**2 + dy**2

        if distancia_quad <= BALL_RADIUS**2:
            dot = bola.vx * normal_x + bola.vy * normal_y
            if dot >= 0:
                continue  # Bola está se movendo para longe

            # Resolver sobreposição
            distancia = math.sqrt(distancia_quad)
            sobreposicao = BALL_RADIUS - distancia
            if distancia > 0:
                bola.x += normal_x * sobreposicao
                bola.y += normal_y * sobreposicao

            # Calcular componentes da velocidade
            componente_normal = dot * normal_x, dot * normal_y
            componente_tangente = (bola.vx - componente_normal[0], 
                                  bola.vy - componente_normal[1])

            # Aplicar restituição e atrito
            nova_normal = (-RESTITUTION * componente_normal[0],
                          -RESTITUTION * componente_normal[1])
            nova_tangente = (FRICTION * componente_tangente[0],
                            FRICTION * componente_tangente[1])

            bola.vx, bola.vy = nova_normal[0] + nova_tangente[0], nova_normal[1] + nova_tangente[1]

    # Desenhar elementos
    tela.fill(BACKGROUND_COLOR)
    pygame.draw.polygon(tela, HEX_COLOR, vertices, 3)
    bola.desenhar(tela)
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()