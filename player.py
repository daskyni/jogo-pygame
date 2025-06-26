import random
import pygame

PLAYER_TOTAL_LIVES = 3
PLAYER_INVULNERABILITY_DURATION = 1000
PLAYER_MELEE_RANGE = 70 # Distância para ataque corpo a corpo
PLAYER_ATTACK_DURATION = 500
PLAYER_ATTACK_COOLDOWN = 1500
PLAYER_KNOCKBACK_DURATION = 200
PLAYER_KNOCKBACK_SPEED = 5
PLAYER_DAMAGE = 1

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.first_walking_sprite_number = 0
        self.last_walking_sprite_number = 7
        self.scale_factor = 3

        self.walk_frames = []
        for i in range(self.first_walking_sprite_number, self.last_walking_sprite_number):
            img_path = f"./sprites/personagens/ceifador/andando/ceifador_andando_{i}.png"
            original_img = pygame.image.load(img_path).convert_alpha()
            scaled_img = pygame.transform.scale(
                original_img,
                (original_img.get_width() * self.scale_factor,
                 original_img.get_height() * self.scale_factor)
            )
            self.walk_frames.append(scaled_img)

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

        self.current_frame = 0
        self.animation_speed = 0.1
        self.attack_animation_speed = PLAYER_ATTACK_DURATION / len(self.attack_frames) / 1000
        self.last_update = 0

        self.image = self.walk_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.image.get_rect().left + 54, self.image.get_rect().top + 30)

        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        hitbox_width = 12 * self.scale_factor
        hitbox_height = 24 * self.scale_factor
        offset_x = 18 * self.scale_factor
        offset_y = 10 * self.scale_factor

        self.hitbox = pygame.Rect(
            self.rect.left + offset_x,
            self.rect.top + offset_y,
            hitbox_width,
            hitbox_height
        )

        self.walking = False
        self.speed = 2
        self.direction_x = 0
        self.direction_y = 0
        self.facing_right = True
        self.direction = pygame.Vector2(1, 0)  # Direção atual para disparo

        self.total_lives = PLAYER_TOTAL_LIVES
        self.lives_remaining = self.total_lives
        self.invulnerable = False
        self.last_hit_time = 0
        self.invulnerable_duration = PLAYER_INVULNERABILITY_DURATION
        self.player_damage = PLAYER_DAMAGE

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = PLAYER_ATTACK_DURATION
        self.last_attack_time = 0
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
        self.current_attack_frame = 0

        self.is_knocked_back = False
        self.knockback_start_time = 0
        self.knockback_direction = pygame.Vector2(0, 0)

        self.base_sprite_image = self.image

    def update(self):
        now = pygame.time.get_ticks()

        # Atualiza o vetor de direção com base no estado do movimento
        # Isso garante que a direção para o projétil esteja sempre correta.
        if self.direction_x != 0 or self.direction_y != 0:
            self.direction.x = self.direction_x
            self.direction.y = self.direction_y
            if self.direction.length_squared() > 0: # Evita normalizar um vetor nulo
                self.direction.normalize_ip()

        if self.is_knocked_back:
            if now - self.knockback_start_time < PLAYER_KNOCKBACK_DURATION:
                self.rect.x += self.knockback_direction.x * PLAYER_KNOCKBACK_SPEED
                self.rect.y += self.knockback_direction.y * PLAYER_KNOCKBACK_SPEED
            else:
                self.is_knocked_back = False
                if self.direction_x == 0 and self.direction_y == 0:
                    self.walking = False
        else:
            self.rect.x += self.direction_x * self.speed
            self.rect.y += self.direction_y * self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

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

        if self.invulnerable:
            if now - self.last_hit_time > self.invulnerable_duration:
                self.invulnerable = False
            else:
                if (now - self.last_hit_time) % 300 < 150:
                    temp_surface = pygame.Surface(self.base_sprite_image.get_size(), pygame.SRCALPHA)
                    temp_surface.fill((0, 0, 0, 0))
                    self.image = temp_surface
                else:
                    self.image = self.base_sprite_image

    def update_hitbox(self, isFacingLeft):
        offset_y = 10 * self.scale_factor
        if isFacingLeft:
            offset_x = 8 * self.scale_factor
        else:
            offset_x = 18 * self.scale_factor

        self.hitbox.topleft = (
            self.rect.left + offset_x,
            self.rect.top + offset_y
        )

    def animate_walk(self):
        now = pygame.time.get_ticks()

        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.walk_frames)

            base_image = self.walk_frames[self.current_frame]

            if not self.facing_right:
                self.image = pygame.transform.flip(base_image, True, False)
                self.update_hitbox(True)
            else:
                self.image = base_image
                self.update_hitbox(False)

    def animate_attack(self):
        now = pygame.time.get_ticks()
        frame_duration = self.attack_duration / len(self.attack_frames)

        if now - self.attack_timer >= (self.current_attack_frame + 1) * frame_duration:
            self.current_attack_frame += 1
            if self.current_attack_frame >= len(self.attack_frames):
                self.is_attacking = False
                self.current_attack_frame = 0
                if self.walking:
                    self.image = self.walk_frames[self.current_frame % len(self.walk_frames)]
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

    def attack(self, scythe_sound):
        now = pygame.time.get_ticks()
        if not self.is_attacking and (now - self.last_attack_time > self.attack_cooldown):
            self.is_attacking = True
            self.attack_timer = now
            self.last_attack_time = now
            self.current_attack_frame = 0
            if scythe_sound:
                scythe_sound.play()
            return True # Ataque iniciado com sucesso
        return False # Ataque em cooldown ou já atacando

    def take_damage(self, amount, damage_source=None):
        if not self.invulnerable:
            self.lives_remaining -= amount
            self.invulnerable = True
            self.last_hit_time = pygame.time.get_ticks()
            if damage_source:
                self.is_knocked_back = True
                self.knockback_start_time = pygame.time.get_ticks()
                knockback_vector = pygame.Vector2(self.rect.center) - pygame.Vector2(damage_source.rect.center)
                if knockback_vector.length_squared() > 0:
                    self.knockback_direction = knockback_vector.normalize()
                else:
                    self.knockback_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if self.knockback_direction.length_squared() > 0:
                        self.knockback_direction.normalize()
                    else:
                        self.knockback_direction = pygame.Vector2(0, -1)

            if self.lives_remaining <= 0:
                self.lives_remaining = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_knocked_back:
                return
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.direction_x = 1
                self.walking = True
                self.facing_right = True
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.direction_x = -1
                self.walking = True
                self.facing_right = False
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.direction_y = -1
                self.walking = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.direction_y = 1
                self.walking = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.direction_x == 1:
                    self.direction_x = 0
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.direction_x == -1:
                    self.direction_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if self.direction_y == -1:
                    self.direction_y = 0
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if self.direction_y == 1:
                    self.direction_y = 0

            if self.direction_x == 0 and self.direction_y == 0 and not self.is_attacking:
                self.walking = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)