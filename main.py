import pygame
from ghosts import Ghost
from player import Player
from projectile import Projectile

# define o FPS do jogo
FPS = 60

# define o tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

def load_smoke_frames():
    frames = []
    for i in range(0, 10):
        img = pygame.image.load(f'./sprites/personagens/ceifador/fumaca/fumaca_{i}.png').convert_alpha()
        frames.append(img)
    return frames

def inicializa_jogo(player, ghosts):
    player.lives_remaining = player.total_lives
    player.life_count_atual = player.life_counters[player.lives_remaining]
    player.walking = False
    player.is_attacking = False
    player.direction_x = 0
    player.direction_y = 0
    player.invulnerable = False
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    for ghost in ghosts:
        ghost.kill()

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("O Jogo do Ceifador")

    background_image_path = "./sprites/mapa/mapa.png"
    background_image = pygame.image.load(background_image_path).convert()
    scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_rect = scaled_background.get_rect()
    background_rect.topleft = (0, 0)

    initial_background_path = "./background/backgroundInitial.png"
    initial_background_image = pygame.image.load(initial_background_path).convert()
    scaled_initial_background = pygame.transform.scale(initial_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    initial_background_rect = scaled_initial_background.get_rect()

    FONT_PATH = "./fonts/Pixel Emulator.otf"
    pygame.font.init()
    try:
        font_stats = pygame.font.Font(FONT_PATH, 20)
        font_title = pygame.font.Font(FONT_PATH, 20)
        font_instruction = pygame.font.Font(FONT_PATH, 25)
    except pygame.error:
        print(f"Aviso: Fonte '{FONT_PATH}' não encontrada. Usando fonte padrão.")
        font_stats = pygame.font.Font(None, 38)
        font_title = pygame.font.Font(None, 76)
        font_instruction = pygame.font.Font(None, 42)

    TELA_INICIAL = "TELA_INICIAL"
    JOGANDO = "JOGANDO"
    GAME_OVER = "GAME_OVER"
    game_state = TELA_INICIAL

    GHOST_SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(GHOST_SPAWN_EVENT, 2000)

    POSICAO_X_LIFE_COUNT = 20
    POSICAO_Y_LIFE_COUNT = 20

    player = Player()
    ghosts = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    smoke_frames = load_smoke_frames()

    last_shot_time = 0
    shot_cooldown = 1500  # ms

    clock = pygame.time.Clock()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == GHOST_SPAWN_EVENT:
                new_ghost = Ghost(player, ghosts)
                ghosts.add(new_ghost)

            if game_state == TELA_INICIAL:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        inicializa_jogo(player, ghosts)
                        game_state = JOGANDO

            elif game_state == JOGANDO:
                player.handle_input(event)

            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        inicializa_jogo(player, ghosts)
                        game_state = JOGANDO
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if game_state == JOGANDO:
            # Disparo automático do projetil
            if current_time - last_shot_time >= shot_cooldown:
                last_shot_time = current_time
                proj = Projectile(player.rect.center, player.direction, smoke_frames)
                projectiles.add(proj)

            projectiles.update()

            # Colisão projetil x fantasmas
            for proj in projectiles:
                hits = pygame.sprite.spritecollide(proj, ghosts, False)
                if hits:
                    for ghost in hits:
                        ghost.take_damage(1)
                    proj.kill()

        # Desenha telas
        if game_state == TELA_INICIAL:
            screen.blit(scaled_initial_background, initial_background_rect)
            instrucao_surface = font_instruction.render("Pressione ENTER para começar", True, (38, 56, 48))
            instrucao_rect = instrucao_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(instrucao_surface, instrucao_rect)

        elif game_state == JOGANDO:
            screen.blit(scaled_background, background_rect)

            player.update()
            player.draw(screen)

            for ghost in ghosts:
                ghost.update()
                ghost.draw(screen)

            projectiles.draw(screen)

            screen.blit(player.life_count_atual, (POSICAO_X_LIFE_COUNT, POSICAO_Y_LIFE_COUNT))

            if player.lives_remaining <= 0:
                game_state = GAME_OVER

        elif game_state == GAME_OVER:
            screen.blit(scaled_initial_background, initial_background_rect)
            game_over_surface = font_title.render("GAME OVER", True, (38, 56, 48))
            instrucao_restart_surface = font_instruction.render("ENTER para reiniciar", True, (38, 56, 48))
            instrucao_sair_surface = font_stats.render("ESC para sair", True, (38, 56, 48))

            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            instrucao_restart_rect = instrucao_restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            instrucao_sair_rect = instrucao_sair_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

            screen.blit(game_over_surface, game_over_rect)
            screen.blit(instrucao_restart_surface, instrucao_restart_rect)
            screen.blit(instrucao_sair_surface, instrucao_sair_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
