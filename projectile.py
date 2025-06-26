import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction_vector, smoke_sprites):
        super().__init__()

        scale_factor = 3 
        
        # Redimensiona os sprites da fumaça
        original_scaled_sprites = [
            pygame.transform.scale(
                img,
                (img.get_width() * scale_factor, img.get_height() * scale_factor)
            ) for img in smoke_sprites
        ]

        # Rotaciona os sprites com base no vetor de direção
        # O sprite original aponta para a direita (ângulo 0)
        # Usamos math.atan2 para um cálculo de ângulo mais robusto.
        # O Y é invertido (-direction_vector.y) por causa do sistema de coordenadas do Pygame.
        angle = math.degrees(math.atan2(-direction_vector.y, direction_vector.x))
        scaled_sprites = [pygame.transform.rotate(img, angle) for img in original_scaled_sprites]

        self.smoke_sprites = scaled_sprites
        self.frame_index = 0
        self.animation_speed = 0.2
        self.frame_counter = 0
        self.speed = 8
        self.direction = direction_vector
        self.image = self.smoke_sprites[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height * 0.3)

    def update(self):
        # Movimento com base no vetor de direção
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # Atualiza a hitbox junto com o rect
        self.hitbox.center = self.rect.center

        # Animação
        self.frame_counter += self.animation_speed
        if self.frame_counter >= 1:
            self.frame_counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.smoke_sprites):
                self.kill()
                return
            self.image = self.smoke_sprites[self.frame_index]

        # Remove se sair da tela
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.kill()
