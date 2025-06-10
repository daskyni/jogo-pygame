import pygame
import random # Para knockback padrão em caso de sobreposição exata
from main import SCREEN_WIDTH, SCREEN_HEIGHT

PLAYER_MAX_HEALTH = 100
PLAYER_INVULNERABILITY_DURATION = 2000  # ms
PLAYER_ATTACK_DURATION = 200  # ms
PLAYER_ATTACK_COOLDOWN = 500  # ms
PLAYER_KNOCKBACK_DURATION = 150 # ms
PLAYER_KNOCKBACK_SPEED = 5


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # variaveis que definem o numero de sprites
        self.first_sprite_number = 0
        self.last_sprite_number = 7

        # fator de escala para a sprite do personagem
        self.scale_factor = 3

        # carrega os frames da animacao de andar
        self.walk_frames = []
        for i in range(self.first_sprite_number, self.last_sprite_number):
            img_path = f"./sprites/personagens/ceifador/andando/ceifador_andando_{i}.png"
            original_img = pygame.image.load(img_path)
            # escala a imagem
            scaled_img = pygame.transform.scale(
                original_img,
                (original_img.get_width() * self.scale_factor,
                    original_img.get_height() * self.scale_factor)
            )
            self.walk_frames.append(scaled_img)

        # variaveis de controle de animacao
        self.current_frame = 0 # frame atual
        self.animation_speed = 0.1
        self.last_update = 0

        # imagem inicial
        self.image = self.walk_frames[self.current_frame]
        self.rect = self.image.get_rect()
        
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # variaveis que controlam o estado do jogador (parado ou andando)
        self.walking = False
        self.speed = 2 # velocidade do jogador
        self.direction_x = 0 # 0 = parado, 1 = direita, -1 = esquerda
        self.direction_y = 0 # 0 = parado, 1 = baixo, -1 = cima
        self.facing_right = True # controla quando o personagem esta olhando para a direita

        # Atributos de combate e vida
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.invulnerable = False
        self.last_hit_time = 0
        self.invulnerable_duration = PLAYER_INVULNERABILITY_DURATION

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = PLAYER_ATTACK_DURATION
        self.last_attack_time = 0
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN

        # Atributos de experiência e nível
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100 # XP necessário para o próximo nível
        self.base_xp_to_next_level = 100 # Base para calcular o próximo nível

        # Atributos de Knockback
        self.is_knocked_back = False
        self.knockback_start_time = 0
        self.knockback_direction = pygame.Vector2(0, 0)

        self.base_sprite_image = self.image # Para referência ao piscar

    # metodo que atualiza a direção do movimento e animação
    def update(self):
        now = pygame.time.get_ticks()

        if self.is_knocked_back:
            if now - self.knockback_start_time < PLAYER_KNOCKBACK_DURATION:
                self.rect.x += self.knockback_direction.x * PLAYER_KNOCKBACK_SPEED
                self.rect.y += self.knockback_direction.y * PLAYER_KNOCKBACK_SPEED
            else:
                self.is_knocked_back = False
        else:
            # Movimento normal do jogador apenas se não estiver em knockback
            self.rect.x += self.direction_x * self.speed
            self.rect.y += self.direction_y * self.speed

        # Mantém o jogador dentro dos limites da tela (aplica-se a ambos os movimentos)
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # colisao com a borda esquerda do mapa
        if self.rect.left < 0:
            self.rect.left = 0

        # colisao com a borda inferior do mapa
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # colisao com a borda superior do mapa
        if self.rect.top < 0:
            self.rect.top = 0

        # Lógica de animação
        if self.walking:
            self.animate_walk() # Isso define self.image
        else:
            # se não estiver andando, mostra o primeiro frame na direção correta
            self.image = self.walk_frames[0]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
        
        self.base_sprite_image = self.image # Guarda a imagem base do frame

        # Lógica de invulnerabilidade e piscar
        if self.invulnerable:
            if now - self.last_hit_time > self.invulnerable_duration:
                self.invulnerable = False
            else:
                # Piscar: alterna visibilidade
                if (now - self.last_hit_time) % 300 < 150: # Invisível por 150ms
                    # Cria uma superfície transparente temporária
                    temp_surface = pygame.Surface(self.base_sprite_image.get_size(), pygame.SRCALPHA)
                    temp_surface.fill((0,0,0,0)) # Totalmente transparente
                    self.image = temp_surface
                else: # Visível por 150ms
                    self.image = self.base_sprite_image
        
        # Gerencia estado de ataque
        if self.is_attacking and (now - self.attack_timer > self.attack_duration):
            self.is_attacking = False

    # metodo que realiza a animacao de andar do personagem
    def animate_walk(self):
        now = pygame.time.get_ticks() # pega quanto tempo se passou desde que a funcao pygame.init() foi chamada

        # verifica se o tempo que passou é maior do que o tempo que cada frame deve ficar na tela
        if now - self.last_update > self.animation_speed * 1000:
            # atualiza o tempo e o frame
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.walk_frames) # realiza o loop dos frames

            # pega o frame base
            base_image = self.walk_frames[self.current_frame]

            # vira a imagem se a direcao for para a esquerda
            if not self.facing_right:
                self.image = pygame.transform.flip(base_image, True, False) # flip_x = True, flip_y = False
            else:
                self.image = base_image # nao vira se estiver para a direita

    # metodo que controla para qual posicao o personagem deve se mover de acordo com o input do usuario
    def handle_input(self, event):
        now = pygame.time.get_ticks()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.direction_x = 1
                self.walking = True
                self.facing_right = True # define que o personagem esta olhando para a direita
            elif event.key == pygame.K_LEFT:
                self.direction_x = -1
                self.walking = True
                self.facing_right = False # define que o personagem esta olhando para a esquerda
            elif event.key == pygame.K_UP:
                self.direction_y = -1
                self.walking = True
            elif event.key == pygame.K_DOWN:
                self.direction_y = 1
                self.walking = True
            elif event.key == pygame.K_SPACE: # Tecla de ataque
                if not self.is_attacking and (now - self.last_attack_time > self.attack_cooldown):
                    self.is_attacking = True
                    self.attack_timer = now
                    self.last_attack_time = now

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and self.direction_x == 1:
                self.direction_x = 0
            elif event.key == pygame.K_LEFT and self.direction_x == -1:
                self.direction_x = 0
            elif event.key == pygame.K_UP and self.direction_y == -1:
                self.direction_y = 0
            elif event.key == pygame.K_DOWN and self.direction_y == 1:
                self.direction_y = 0

            if self.direction_x == 0 and self.direction_y == 0:
                self.walking = False

    def take_damage(self, amount, damage_source=None):
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.last_hit_time = pygame.time.get_ticks()
            print(f"Player health: {self.health}") # Para debug

            # Lógica de Knockback
            if damage_source:
                self.is_knocked_back = True
                self.knockback_start_time = pygame.time.get_ticks()
                # Calcula a direção do knockback (para longe da fonte de dano)
                knockback_vector = pygame.Vector2(self.rect.center) - pygame.Vector2(damage_source.rect.center)
                if knockback_vector.length_squared() > 0: # Evita erro com vetor zero
                    self.knockback_direction = knockback_vector.normalize()
                else: # Caso raro de sobreposição exata de centros, usa uma direção aleatória
                    self.knockback_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if self.knockback_direction.length_squared() > 0:
                        self.knockback_direction.normalize()
                    else: # Se ainda for zero (extremamente raro), um padrão para cima
                        self.knockback_direction = pygame.Vector2(0, -1)

            if self.health <= 0:
                self.health = 0
                print("Player Died!") # Lógica de game over pode vir aqui
    def gain_xp(self, amount):
        self.xp += amount
        print(f"Player gained {amount} XP. Total XP: {self.xp}/{self.xp_to_next_level}") # Para debug
        while self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            # Aumenta a XP necessária para o próximo nível (ex: 50% a mais que o anterior)
            self.xp_to_next_level = int(self.base_xp_to_next_level * (1.5 ** (self.level -1))) # Ou uma fórmula mais simples: self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            print(f"Player leveled up to Level {self.level}! XP for next level: {self.xp_to_next_level}")
            # Aqui você pode adicionar bônus por subir de nível, como aumentar max_health, dano, etc.
            # Ex: self.max_health += 10; self.health = self.max_health
