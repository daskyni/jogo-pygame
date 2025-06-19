import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, smoke_sprites):
        super().__init__()

        scale_factor = 3 
        
        # Redimensiona os sprites da fumaça
        scaled_sprites = [
            pygame.transform.scale(
                img,
                (img.get_width() * scale_factor, img.get_height() * scale_factor)
            ) for img in smoke_sprites
        ]

        # Ajusta sprites conforme direção
        if direction == 'left':
            scaled_sprites = [pygame.transform.flip(img, True, False) for img in scaled_sprites]
        elif direction == 'up':
            scaled_sprites = [pygame.transform.rotate(img, 90) for img in scaled_sprites]
        elif direction == 'down':
            scaled_sprites = [pygame.transform.rotate(img, -90) for img in scaled_sprites]

        self.smoke_sprites = scaled_sprites
        self.frame_index = 0
        self.animation_speed = 0.2
        self.frame_counter = 0
        self.speed = 8
        self.direction = direction
        self.image = self.smoke_sprites[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        # Movimento conforme direção
        if self.direction == 'right':
            self.rect.x += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed

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
