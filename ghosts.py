import math
import pygame
import random
from main import SCREEN_WIDTH, SCREEN_HEIGHT

# Constantes para o fantasma
GHOST_CONTACT_DAMAGE = 1
GHOST_TOTAL_LIVES = 1
GHOST_AGGRO_RADIUS = 200 # Raio em que o fantasma começa a perseguir o Player
MIN_PLAYER_DISTANCE = 200 # Ajustado para evitar dano "de longe"

# Constantes para repulsão entre fantasmas
MIN_GHOST_DISTANCE_REPEL = 50  # Distância para começar a repelir (ajuste conforme o tamanho do sprite)
GHOST_REPEL_STRENGTH_VALUE = 0.5 # Força da repulsão (pequeno valor para evitar movimentos bruscos)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, player, all_ghosts_group):
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
        
        # define onde o fantasma vai nascer aleatoriamente
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT
        elif side == 'left':
            x = 0
            y = random.randint(0, SCREEN_HEIGHT)
        else:  # right
            x = SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT)

        self.rect.center = (x, y)

        # velocidade de movimento
        self.speed = 0.5

        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.player = player
        self.all_ghosts_group = all_ghosts_group # Grupo de todos os fantasmas para checar repulsão

        self.timer = 0
        self.change_direction_time = random.randint(60, 120)

        self.total_lives = GHOST_TOTAL_LIVES
        self.lives_remaining = self.total_lives
    
    def update(self):
        self.animate_fluctuate()

        # Lógica de Comportamento (Direção e Velocidade)
        distance_vector = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        # Calcula a distância, tratando o caso de vetor zero para evitar erros com .length()
        distance_length = distance_vector.length() if distance_vector.length_squared() > 0 else 0

        # Define a velocidade base do fantasma dependendo se o jogador está andando
        current_speed = 1.5 if self.player.walking else 0.8 # ajustado para fantasma ser mais lento que o jogador

        # Comportamento de Perseguição / Proximidade
        if distance_length < GHOST_AGGRO_RADIUS:  # Dentro do raio de agressão
            if distance_length <= MIN_PLAYER_DISTANCE:
                # Muito perto: para o fantasma (velocidade = 0).
                # A direção atual será mantida, mas a velocidade será zero.
                # O timer de movimento aleatório continua, então a direção pode mudar,
                # mas ele só se moverá se o jogador se afastar.
                current_speed = 0
                # O timer de movimento aleatório continua rodando para que, se o jogador se afastar,
                # o fantasma não fique preso na direção antiga.
                self.timer += 1
                if self.timer >= self.change_direction_time:
                    self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                    self.change_direction_time = random.randint(60, 120) # Frames
                    self.timer = 0
            else: # Dentro do raio de aggro, mas não muito perto: persegue o jogador
                if distance_vector.length_squared() > 0: # Normaliza apenas se o vetor não for zero
                    self.direction = distance_vector.normalize()
                # Reseta o timer de movimento aleatório, já que está perseguindo ativamente
                self.timer = 0 
        else:
            # Fora do raio de agressão: movimento aleatório
            self.timer += 1
            if self.timer >= self.change_direction_time:
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                self.change_direction_time = random.randint(60, 120) # Frames
                self.timer = 0
        
        # Movimento base calculado
        base_move_x = self.direction.x * current_speed
        base_move_y = self.direction.y * current_speed

        # Lógica de repulsão entre fantasmas
        repel_offset = pygame.Vector2(0, 0)
        if self.all_ghosts_group:
            for other_ghost in self.all_ghosts_group:
                if other_ghost != self: # Não se repele
                    # Vetor do centro deste fantasma para o centro do outro fantasma
                    vec_from_self_to_other = pygame.Vector2(other_ghost.rect.centerx - self.rect.centerx,
                                                            other_ghost.rect.centery - self.rect.centery)
                    distance = vec_from_self_to_other.length()

                    if 0 < distance < MIN_GHOST_DISTANCE_REPEL:
                        # Se muito perto, calcula um pequeno empurrão para longe do outro fantasma (na direção oposta ao vetor)
                        # Normaliza o vetor (que aponta para o outro fantasma) e inverte para obter a direção de afastamento
                        if distance == 0: # Evita divisão por zero se estiverem exatamente no mesmo lugar
                             # Aplica um empurrão aleatório para longe
                            push_away_direction = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
                        else:
                            push_away_direction = -vec_from_self_to_other.normalize()
                        repel_offset += push_away_direction * GHOST_REPEL_STRENGTH_VALUE

        # limitar na tela
        self.rect.x += base_move_x + repel_offset.x
        self.rect.y += base_move_y + repel_offset.y
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # verificar colisão com player
        if self.rect.colliderect(self.player.hitbox):
            # O fantasma causa dano ao jogador ao tocá-lo.
            # A lógica de invulnerabilidade do jogador esta em player.take_damage()
            self.player.take_damage(GHOST_CONTACT_DAMAGE, self) # Passa o fantasma como fonte do dano

    def animate_fluctuate(self):
        now = pygame.time.get_ticks()

        # verifica se o tempo que passou é maior do que o tempo que cada frame deve ficar na tela
        if now - self.last_update > self.animation_speed * 1000:
            # atualiza o tempo e o frame
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.fluctuate_frames) # realiza o loop dos frames
        
            # pega o frame base
            base_image = self.fluctuate_frames[self.current_frame]
            self.image = base_image

    def take_damage(self, amount):
        self.lives_remaining -= amount
        if self.lives_remaining <= 0:
            self.kill()  # remove o fantasma do grupo e da tela

    def draw(self, surface):
        surface.blit(self.image, self.rect)
