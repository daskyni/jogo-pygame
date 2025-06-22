import math
import pygame
import random

# Constantes para o fantasma
GHOST_CONTACT_DAMAGE = 1
GHOST_TOTAL_LIVES = 1
GHOST_AGGRO_RADIUS = 400  # Raio em que o fantasma começa a perseguir o Player
MIN_PLAYER_DISTANCE = 30

# Constantes para repulsão entre fantasmas
MIN_GHOST_DISTANCE_REPEL = 200  # Distância para começar a repelir (ajuste conforme o tamanho do sprite)
GHOST_REPEL_STRENGTH_VALUE = 0.5  # Força da repulsão (pequeno valor para evitar movimentos bruscos)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

GHOST_SPAWN_POINTS = [
    (SCREEN_WIDTH // 2, 0),               # meio do topo
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT),   # meio da base
    (0, SCREEN_HEIGHT // 2),               # meio da esquerda
    (SCREEN_WIDTH, SCREEN_HEIGHT // 2)    # meio da direita
]

class Ghost(pygame.sprite.Sprite):
    def __init__(self, player, all_ghosts_group, spawn_pos=None):
        super().__init__()

        # sprites de flutuar
        self.first_fluctuating_sprite_number = 0
        self.last_fluctuating_sprite_number = 3

        # fator de escala para sprite do fantasma
        self.scale_factor = 3

        self.fluctuate_frames = []
        for i in range(self.first_fluctuating_sprite_number, self.last_fluctuating_sprite_number):
            img_path = f"./sprites/personagens/fantasma/flutuando/fantasma_flutuando_{i}.png"
            original_img = pygame.image.load(img_path).convert_alpha()
            # escala a imagem
            scaled_img = pygame.transform.scale(
                original_img,
                (original_img.get_width() * self.scale_factor,
                 original_img.get_height() * self.scale_factor)
            )
            self.fluctuate_frames.append(scaled_img)

        # variaveis de controle de animacao
        self.current_frame = 0
        self.animation_speed = 0.3
        self.last_update = 0

        # imagem inicial
        self.image = self.fluctuate_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-self.rect.width * 0.3, -self.rect.height * 0.3)  # reduz 30%

        # Se spawn_pos não for fornecida, escolhe aleatoriamente entre as 4 fixas
        if spawn_pos is None:
            spawn_pos = random.choice(GHOST_SPAWN_POINTS)
        self.rect.center = spawn_pos

        # velocidade de movimento
        self.speed = 0.5

        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.player = player
        self.all_ghosts_group = all_ghosts_group  # Grupo de todos os fantasmas para checar repulsão

        self.timer = 0
        self.change_direction_time = random.randint(60, 120)

        self.total_lives = GHOST_TOTAL_LIVES
        self.lives_remaining = self.total_lives

    def update(self):
        self.animate_fluctuate()

        # Lógica de Comportamento (Direção e Velocidade)
        distance_vector = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        distance_length = distance_vector.length() if distance_vector.length_squared() > 0 else 0

        current_speed = 1.5 if self.player.walking else 0.8

        if distance_length < GHOST_AGGRO_RADIUS:
            if distance_length <= MIN_PLAYER_DISTANCE:
                current_speed = 0
                self.timer += 1
                if self.timer >= self.change_direction_time:
                    self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                    self.change_direction_time = random.randint(60, 120)
                    self.timer = 0
            else:
                if distance_vector.length_squared() > 0:
                    self.direction = distance_vector.normalize()
                self.timer = 0
        else:
            self.timer += 1
            if self.timer >= self.change_direction_time:
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                self.change_direction_time = random.randint(60, 120)
                self.timer = 0

        base_move_x = self.direction.x * current_speed
        base_move_y = self.direction.y * current_speed

        repel_offset = pygame.Vector2(0, 0)
        if self.all_ghosts_group:
            for other_ghost in self.all_ghosts_group:
                if other_ghost != self:
                    vec_from_self_to_other = pygame.Vector2(other_ghost.rect.centerx - self.rect.centerx,
                                                            other_ghost.rect.centery - self.rect.centery)
                    distance = vec_from_self_to_other.length()

                    if 0 < distance < MIN_GHOST_DISTANCE_REPEL:
                        if distance == 0:
                            push_away_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                        else:
                            push_away_direction = -vec_from_self_to_other.normalize()
                        repel_offset += push_away_direction * GHOST_REPEL_STRENGTH_VALUE

        self.rect.x += base_move_x + repel_offset.x
        self.rect.y += base_move_y + repel_offset.y
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.rect.colliderect(self.player.hitbox):
            self.player.take_damage(GHOST_CONTACT_DAMAGE, self)

    def animate_fluctuate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.fluctuate_frames)
            base_image = self.fluctuate_frames[self.current_frame]
            self.image = base_image

    def take_damage(self, amount):
        self.lives_remaining -= amount
        if self.lives_remaining <= 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
