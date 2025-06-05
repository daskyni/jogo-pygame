import pygame

# define o FPS do jogo
FPS = 60

# define o tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

if __name__ == "__main__":
    
    # importa classes
    from player import Player

    # incia o pygame
    pygame.init()

    # definicoes gerais da screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The Reaper Game")
    background_image_path = "./sprites/mapa/mapa_completo.png"
    background_image = pygame.image.load(background_image_path).convert()
    # aplica a transformação de scale para adequar o background ao tamanho da screen
    scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_rect = scaled_background.get_rect()
    background_rect.topleft = (0, 0)

    # adiciona as sprites
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # clock para controlar o framerate
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # controla eventos do player
            player.handle_input(event)

        # coloca o background na tela
        screen.blit(scaled_background, background_rect)

        # adiciona o grupo de sprites
        all_sprites.update()
        all_sprites.draw(screen)

        # atualiza a tela
        pygame.display.flip()

        # define o FPS da screen
        clock.tick(FPS)

    pygame.quit()
