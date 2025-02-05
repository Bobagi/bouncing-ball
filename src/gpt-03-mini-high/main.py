import pygame
import math
import sys

# Configurações da janela e física
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5          # aceleração gravitacional
AIR_FRICTION = 0.99    # atrito do ar (reduz a velocidade aos poucos)
ELASTICITY = 0.9       # fator de restituição nas colisões (simula perda de energia)
HEXAGON_RADIUS = 200
HEXAGON_CENTER = (WIDTH // 2, HEIGHT // 2)
ROTATION_SPEED = 0.02  # velocidade de rotação do hexágono em radianos por frame

class Ball:
    def __init__(self, x, y, radius):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(5, 0)  # velocidade inicial
        self.radius = radius

    def update(self):
        # Aplica gravidade e atrito do ar
        self.vel.y += GRAVITY
        self.pos += self.vel
        self.vel *= AIR_FRICTION

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), self.radius)

def get_hexagon_vertices(center, radius, angle_offset):
    """Retorna a lista de vértices do hexágono, aplicando uma rotação de angle_offset."""
    cx, cy = center
    vertices = []
    for i in range(6):
        angle = angle_offset + i * (math.pi / 3)  # 60° em radianos
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def check_collision(ball, p1, p2):
    """
    Verifica e trata a colisão da bola com o segmento de reta formado por p1 e p2.
    Se houver colisão, reflete a velocidade da bola de acordo com a normal da parede.
    """
    p1_vec = pygame.math.Vector2(p1)
    p2_vec = pygame.math.Vector2(p2)
    # Vetor do segmento e do centro da bola até p1
    line_vec = p2_vec - p1_vec
    ball_to_p1 = ball.pos - p1_vec

    # Projeta o vetor da bola sobre o segmento
    line_length = line_vec.length()
    if line_length == 0:
        return  # evita divisão por zero
    line_dir = line_vec.normalize()
    projection_length = ball_to_p1.dot(line_dir)
    # Limita a projeção para o segmento (entre 0 e o comprimento do segmento)
    projection_length = max(0, min(line_length, projection_length))
    closest_point = p1_vec + projection_length * line_dir

    # Verifica se a distância entre o centro da bola e o ponto mais próximo é menor que o raio
    distance = (ball.pos - closest_point).length()
    if distance < ball.radius:
        # Calcula a normal (vetor de colisão) a partir do ponto de contato
        if distance == 0:
            normal = pygame.math.Vector2(0, -1)
        else:
            normal = (ball.pos - closest_point).normalize()
        # Se a bola estiver se movendo em direção à parede, reflete a velocidade
        if ball.vel.dot(normal) < 0:
            ball.vel = ball.vel - 2 * ball.vel.dot(normal) * normal
            ball.vel *= ELASTICITY
            # Corrige a posição para que a bola não fique "presa" na parede
            overlap = ball.radius - distance
            ball.pos += normal * overlap

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bola Quicando no Hexágono Giratório")
    clock = pygame.time.Clock()

    ball = Ball(HEXAGON_CENTER[0], HEXAGON_CENTER[1] - 100, 10)
    rotation_angle = 0

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Atualiza a posição e velocidade da bola
        ball.update()

        # Atualiza o ângulo de rotação do hexágono
        rotation_angle += ROTATION_SPEED
        vertices = get_hexagon_vertices(HEXAGON_CENTER, HEXAGON_RADIUS, rotation_angle)

        # Verifica colisões da bola com cada lado do hexágono
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            check_collision(ball, p1, p2)

        # Desenha a cena
        screen.fill((255, 255, 255))  # fundo branco
        pygame.draw.polygon(screen, (0, 0, 255), vertices, 3)  # desenha o hexágono (contorno azul)
        ball.draw(screen)  # desenha a bola
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
