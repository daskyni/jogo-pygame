import random
import pygame
from main import SCREEN_WIDTH, SCREEN_HEIGHT

# constantes do player
PLAYER_TOTAL_LIVES = 3
PLAYER_INVULNERABILITY_DURATION = 1000
PLAYER_ATTACK_DURATION = 500
PLAYER_ATTACK_COOLDOWN = 1500 # ataca a cada 2s
PLAYER_KNOCKBACK_DURATION = 200
PLAYER_KNOCKBACK_SPEED = 5
PLAYER_DAMAGE = 1

# tamanho do life count
TAMANHO_COMPRIMENTO_LIFE_COUNT = 150
TAMANHO_ALTURA_LIFE_COUNT = 50

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
    
        # sprites de andar
        self.first_walking_sprite_number = 0
        self.last_walking_sprite_number = 7

        # fator de escala para a sprite do personagem
        self.scale_factor = 3

        # carrega os frames da animacao de andar
        self.walk_frames = []
        for i in range(self.first_walking_sprite_number, self.last_walking_sprite_number):
            img_path = f"./sprites/personagens/ceifador/andando/ceifador_andando_{i}.png"
            original_img = pygame.image.load(img_path).convert_alpha()
            # escala a imagem
            scaled_img = pygame.transform.scale(
                original_img,
                (original_img.get_width() * self.scale_factor,
                 original_img.get_height() * self.scale_factor)
            )
            self.walk_frames.append(scaled_img)

        # sprites de ataque
        self.first_attack_sprite_number = 0
        self.last_attack_sprite_number = 7
        self.attack_frames = []
        for i in range(self.first_attack_sprite_number, self.last_attack_sprite_number):
            img_path = f"./sprites/personagens/ceifador/atacando/ceifador_atacando_{i}.png"
            original_img = pygame.image.load(img_path).convert_alpha()
            scaled_img = pygame.transform.scale(
                original_img,
                (original_img.get_width() * self.scale_factor,
                 original_img.get_height() * self.scale_factor)
            )
            self.attack_frames.append(scaled_img)    

        # variaveis de controle de animacao
        self.current_frame = 0 # frame atual
        self.animation_speed = 0.1
        self.attack_animation_speed = PLAYER_ATTACK_DURATION / len(self.attack_frames) / 1000
        self.last_update = 0

        # imagem inicial
        self.image = self.walk_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.image.get_rect().left + 54, self.image.get_rect().top + 30)
        
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # criar hitbox separada (menor, só pega o corpo)
        hitbox_width = 12 * self.scale_factor   # 12 → 36 px
        hitbox_height = 24 * self.scale_factor  # 24 → 72 px
        offset_x = 18 * self.scale_factor       # deslocamento lateral do corpo
        offset_y = 10 * self.scale_factor       # deslocamento vertical do corpo

        # ajusta hitbox com base na posição da imagem
        self.hitbox = pygame.Rect(
            self.rect.left + offset_x,
            self.rect.top + offset_y,
            hitbox_width,
            hitbox_height
        )

        # variaveis que controlam o estado do jogador (parado ou andando)
        self.walking = False
        self.speed = 2 # velocidade do jogador
        self.direction_x = 0 # 0 = parado, 1 = direita, -1 = esquerda
        self.direction_y = 0 # 0 = parado, 1 = baixo, -1 = cima
        self.facing_right = True # controla quando o personagem esta olhando para a direita

        # atributos de combate e vida
        self.total_lives = PLAYER_TOTAL_LIVES
        self.lives_remaining = self.total_lives
        self.invulnerable = False
        self.last_hit_time = 0
        self.invulnerable_duration = PLAYER_INVULNERABILITY_DURATION
        self.player_damage = PLAYER_DAMAGE

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = PLAYER_ATTACK_DURATION
        self.last_attack_time = 0 # O tempo do último ataque é crucial para o cooldown
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
        self.current_attack_frame = 0

        # atributos de Knockback
        self.is_knocked_back = False
        self.knockback_start_time = 0
        self.knockback_direction = pygame.Vector2(0, 0)

        self.base_sprite_image = self.image

        # imagens que mostram o numero de vidas do Player
        self.life_count_sprite_3 = pygame.transform.scale(pygame.image.load('./sprites/tela/vida/vida_3.png').convert_alpha(), 
                                            (TAMANHO_COMPRIMENTO_LIFE_COUNT, TAMANHO_ALTURA_LIFE_COUNT))
        self.life_count_sprite_2 = pygame.transform.scale(pygame.image.load('./sprites/tela/vida/vida_2.png').convert_alpha(), 
                                            (TAMANHO_COMPRIMENTO_LIFE_COUNT, TAMANHO_ALTURA_LIFE_COUNT))
        self.life_count_sprite_1 = pygame.transform.scale(pygame.image.load('./sprites/tela/vida/vida_1.png').convert_alpha(), 
                                            (TAMANHO_COMPRIMENTO_LIFE_COUNT, TAMANHO_ALTURA_LIFE_COUNT))
        self.life_count_sprite_0 = pygame.transform.scale(pygame.image.load('./sprites/tela/vida/vida_0.png').convert_alpha(), 
                                            (TAMANHO_COMPRIMENTO_LIFE_COUNT, TAMANHO_ALTURA_LIFE_COUNT))
        
        self.life_counters = [self.life_count_sprite_0, self.life_count_sprite_1, self.life_count_sprite_2, self.life_count_sprite_3]
        
        self.life_count_atual = self.life_counters[self.lives_remaining]


    # metodo que atualiza a direção do movimento e animação
    def update(self):
        now = pygame.time.get_ticks()

        # logica de knockback
        if self.is_knocked_back:
            if now - self.knockback_start_time < PLAYER_KNOCKBACK_DURATION:
                self.rect.x += self.knockback_direction.x * PLAYER_KNOCKBACK_SPEED
                self.rect.y += self.knockback_direction.y * PLAYER_KNOCKBACK_SPEED
            else:
                self.is_knocked_back = False
                if self.direction_x == 0 and self.direction_y == 0:
                    self.walking = False
        else:
            # movimento normal do jogador apenas se não estiver em knockback
            self.rect.x += self.direction_x * self.speed
            self.rect.y += self.direction_y * self.speed

        # mantém o jogador dentro dos limites da tela
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # lógica para o ataque automático
        if not self.is_knocked_back and not self.is_attacking and (now - self.last_attack_time > self.attack_cooldown):
            self.is_attacking = True
            self.attack_timer = now
            self.last_attack_time = now # reinicia o timer do cooldown
            self.current_attack_frame = 0 # começa a animação do ataque do zero

        # logica de animação (prioriza ataque)
        if self.is_attacking:
            self.animate_attack()
        elif self.walking:
            self.animate_walk()
        else:
            self.image = self.walk_frames[0]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.update_hitbox(True)
        
        self.base_sprite_image = self.image

        # logica de invulnerabilidade e piscar ao receber ataque
        if self.invulnerable:
            if now - self.last_hit_time > self.invulnerable_duration:
                self.invulnerable = False
            else:
                # piscar
                if (now - self.last_hit_time) % 300 < 150: # invisivel por 150ms
                    # cria uma superfície transparente temporária
                    temp_surface = pygame.Surface(self.base_sprite_image.get_size(), pygame.SRCALPHA)
                    temp_surface.fill((0,0,0,0)) # transparente
                    self.image = temp_surface
                else: # visivel por 150ms
                    self.image = self.base_sprite_image

    # metodo que atualiza a hitbox com base no scale_factor
    def update_hitbox(self, isFacingLeft):
        offset_y = 10 * self.scale_factor
        if isFacingLeft:
            offset_x = 8 * self.scale_factor  # mais à esquerda
        else:
            offset_x = 18 * self.scale_factor  # mais à direita

        self.hitbox.topleft = (
            self.rect.left + offset_x,
            self.rect.top + offset_y
        )

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
                self.update_hitbox(True)
            else:
                self.image = base_image # nao vira se estiver para a direita
                self.update_hitbox(False)

    def animate_attack(self):
        now = pygame.time.get_ticks() # pega quanto tempo se passou desde que a funcao pygame.init() foi chamada

        frame_duration = self.attack_duration / len(self.attack_frames)

        # verifica se o tempo que passou é maior do que o tempo que cada frame deve ficar na tela
        if now - self.attack_timer >= (self.current_attack_frame + 1) * frame_duration:
            self.current_attack_frame += 1
            if self.current_attack_frame >= len(self.attack_frames):
                self.is_attacking = False
                self.current_attack_frame = 0 # reseta para proximo ataque
                # retorna para a animação de andar/parado
                if self.walking:
                    self.image = self.walk_frames[self.current_frame % len(self.walk_frames)] # garante que o frame seja valido
                else:
                    self.image = self.walk_frames[0]
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.update_hitbox(True)
                return

            base_image = self.attack_frames[self.current_attack_frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(base_image, True, False)
                self.update_hitbox(True)
            else:
                self.image = base_image
                self.update_hitbox(False)    

    def take_damage(self, amount, damage_source=None):
        if not self.invulnerable:
            self.lives_remaining -= amount
            self.life_count_atual = self.life_counters[self.lives_remaining]
            self.invulnerable = True
            self.last_hit_time = pygame.time.get_ticks()
            print(f"Vidas restantes: {self.lives_remaining}") # Para debug
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

            if self.lives_remaining <= 0:
                self.lives_remaining = 0
                print("O Jogador Morreu!") # fazer logica de game over aqui

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_knocked_back:
                return
            if event.key == pygame.K_RIGHT:
                self.direction_x = 1
                self.walking = True
                self.facing_right = True
            elif event.key == pygame.K_LEFT:
                self.direction_x = -1
                self.walking = True
                self.facing_right = False
            elif event.key == pygame.K_UP:
                self.direction_y = -1
                self.walking = True
            elif event.key == pygame.K_DOWN:
                self.direction_y = 1
                self.walking = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and self.direction_x == 1:
                self.direction_x = 0
            elif event.key == pygame.K_LEFT and self.direction_x == -1:
                self.direction_x = 0
            elif event.key == pygame.K_UP and self.direction_y == -1:
                self.direction_y = 0
            elif event.key == pygame.K_DOWN and self.direction_y == 1:
                self.direction_y = 0

            if self.direction_x == 0 and self.direction_y == 0 and not self.is_attacking:
                self.walking = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)