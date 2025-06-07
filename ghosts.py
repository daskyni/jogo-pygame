import pygame
import random
from main import SCREEN_WIDTH, SCREEN_HEIGHT

GHOST_CONTACT_DAMAGE = 10 # Dano que o fantasma causa ao player ao contato

# Constantes para a barra de vida do fantasma
HEALTH_BAR_WIDTH = 30
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_OFFSET_Y = 8  # Distância vertical acima da imagem do fantasma
HEALTH_BAR_BG_COLOR = (150, 0, 0)    # Vermelho escuro para o fundo
HEALTH_BAR_FG_COLOR = (0, 255, 0)    # Verde para a vida atual
HEALTH_BAR_BORDER_COLOR = (0, 0, 0)  # Preto para a borda

# Constantes para o efeito de flash ao ser atingido
HIT_FLASH_DURATION = 100  # ms, duração do flash
HIT_FLASH_STRENGTH = (150, 150, 150) # Cor a ser adicionada para o flash (branco suave)

GHOST_AGGRO_RADIUS = 200 # Raio em que o fantasma começa a perseguir
# Distância mínima para o fantasma parar.
# Este valor deve ser ajustado com base nas dimensões dos sprites do jogador e do fantasma
# para garantir que seus retângulos de colisão não se sobreponham quando o fantasma para.
MIN_PLAYER_DISTANCE = 3 # Ajustado para evitar dano "de longe"

# Constantes para repulsão entre fantasmas
MIN_GHOST_DISTANCE_REPEL = 50  # Distância para começar a repelir (ajuste conforme o tamanho do sprite)
GHOST_REPEL_STRENGTH_VALUE = 0.5 # Força da repulsão (pequeno valor para evitar movimentos bruscos)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, player, ghost_images, all_ghosts_group):
        super().__init__()
        self.images = ghost_images
        self.image_index = 0
        self.image = self.images[self.image_index]

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(100, 700), random.randint(100, 500))

        self.speed = 1.2
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.player = player
        self.all_ghosts_group = all_ghosts_group # Grupo de todos os fantasmas para checar repulsão

        self.timer = 0
        self.change_direction_time = random.randint(60, 120)

        self.animation_timer = 0
        self.animation_speed = 10

        self.max_health = 100
        self.health = 100
        self.invulnerable = False
        self.invulnerable_time = 1000  # em milissegundos
        self.last_hit_time = 0
        self.xp_reward = 25 # Quantidade de XP que este fantasma concede
        
        self.is_hit_flashing = False # Controla se o fantasma está no efeito de flash de acerto
        self.hit_flash_start_time = 0

    def update(self):
        now = pygame.time.get_ticks()

        # 1. Atualiza o índice da animação
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = 0
        
        # 2. Pega a imagem base da animação para este frame
        base_image_for_frame = self.images[self.image_index]
        
        # 3. Aplica efeitos visuais
        # Começa com a imagem base
        final_image = base_image_for_frame

        # Efeito de "hit flash" (branco)
        if self.is_hit_flashing:
            if now - self.hit_flash_start_time < HIT_FLASH_DURATION:
                flash_image = base_image_for_frame.copy()
                flash_image.fill(HIT_FLASH_STRENGTH, special_flags=pygame.BLEND_RGB_ADD)
                final_image = flash_image # O flash tem prioridade sobre a imagem base
            else:
                self.is_hit_flashing = False # Desativa o flash após a duração

        # Efeito de invulnerabilidade (piscar transparente)
        # Este efeito pode sobrescrever a imagem (mesmo que tenha flash) para torná-la transparente
        if self.invulnerable:
            if (now - self.last_hit_time) % 200 < 100: # Fase "invisível" do piscar
                transparent_surface = pygame.Surface(base_image_for_frame.get_size(), pygame.SRCALPHA)
                transparent_surface.fill((0,0,0,0)) # Totalmente transparente
                final_image = transparent_surface
            # Na fase "visível" do piscar, final_image já é a correta (base ou com flash)
        
        self.image = final_image

        # 4. Verifica se deve parar de ser invulnerável (após todos os efeitos visuais do frame)
        if self.invulnerable and now - self.last_hit_time > self.invulnerable_time:
            self.invulnerable = False
            # self.is_hit_flashing já terá sido desativado pelo seu próprio timer
        
        # Lógica de Comportamento (Direção e Velocidade)
        distance_vector = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        # Calcula a distância, tratando o caso de vetor zero para evitar erros com .length()
        distance_length = distance_vector.length() if distance_vector.length_squared() > 0 else 0

        # Define a velocidade base do fantasma dependendo se o jogador está andando
        current_speed = 1.5 if self.player.walking else 0.8 # Ajustado para ser mais lento que o jogador

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
        if self.rect.colliderect(self.player.rect):
            # O fantasma causa dano ao jogador ao tocá-lo.
            # A lógica de invulnerabilidade do jogador já está em player.take_damage()
            self.player.take_damage(GHOST_CONTACT_DAMAGE, self) # Passa o fantasma como fonte do dano

    def take_damage(self, amount):
        if not self.invulnerable: # Só toma dano e mostra efeito se não estiver invulnerável
            self.health -= amount
            current_time = pygame.time.get_ticks()
            self.invulnerable = True
            self.last_hit_time = current_time

            self.is_hit_flashing = True # Ativa o flash de acerto
            self.hit_flash_start_time = current_time # Pode usar o mesmo tempo do início da invulnerabilidade

            if self.health <= 0:
                self.player.gain_xp(self.xp_reward) # Concede XP ao jogador
                self.kill()  # remove o fantasma do grupo e da tela

    def draw_health_bar(self, surface):
        # Desenha a barra de vida apenas se o fantasma estiver vivo e com vida abaixo do máximo
        if self.health > 0 and self.health < self.max_health:
            health_ratio = self.health / self.max_health

            # Posição da barra de vida
            bar_x = self.rect.centerx - HEALTH_BAR_WIDTH // 2
            bar_y = self.rect.top - HEALTH_BAR_OFFSET_Y - HEALTH_BAR_HEIGHT

            # Retângulo da borda
            border_rect = pygame.Rect(bar_x - 1, bar_y - 1, HEALTH_BAR_WIDTH + 2, HEALTH_BAR_HEIGHT + 2)
            pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)

            # Retângulo de fundo da barra de vida
            bg_bar_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_bar_rect)

            # Retângulo da vida atual
            current_health_width = int(HEALTH_BAR_WIDTH * health_ratio)
            health_bar_rect = pygame.Rect(bar_x, bar_y, current_health_width, HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, HEALTH_BAR_FG_COLOR, health_bar_rect)
