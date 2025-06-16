import pygame

# define o FPS do jogo
FPS = 60

# define o tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

if __name__ == "__main__":

    # importa classes
    from ghosts import Ghost
    from player import Player

    # incia o pygame
    pygame.init()

    # definicoes gerais da screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("O Jogo do Ceifador")
    background_image_path = "./sprites/mapa/mapa_completo.png"
    background_image = pygame.image.load(background_image_path).convert()
    # aplica a transformação de scale para adequar o background ao tamanho da screen
    scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_rect = scaled_background.get_rect()
    background_rect.topleft = (0, 0)

    # Carrega e escala a imagem de fundo para tela inicial e game over
    initial_background_path = "./background/backgroundInitial.png" # Certifique-se que o caminho está correto
    initial_background_image = pygame.image.load(initial_background_path).convert()
    scaled_initial_background = pygame.transform.scale(initial_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    initial_background_rect = scaled_initial_background.get_rect()

    FONT_PATH = "./fonts/Pixel Emulator.otf" 
    pygame.font.init() # Garante que o módulo de fontes está inicializado
    try:
        font_stats = pygame.font.Font(FONT_PATH, 20) # Para HP, XP, Nível - Aumentado
        font_title = pygame.font.Font(FONT_PATH, 20)  # Para títulos como "Game Over" - Aumentado
        font_instruction = pygame.font.Font(FONT_PATH, 25) # Para instruções - Levemente diminuído
    except pygame.error: # Caso a fonte não seja encontrada, usa a padrão
        print(f"Aviso: Fonte '{FONT_PATH}' não encontrada. Usando fonte padrão.")
        font_stats = pygame.font.Font(None, 38) # Ajustado para o fallback
        font_title = pygame.font.Font(None, 76) # Ajustado para o fallback
        font_instruction = pygame.font.Font(None, 42) # Ajustado para o fallback

    def inicializa_jogo(player, ghosts_group):
        player.lives_remaining = player.total_lives
        player.life_count_atual = player.life_counters[player.lives_remaining]
        player.walking = False
        player.is_attacking = False
        player.direction_x = 0
        player.direction_y = 0
        player.invulnerable = False
        player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        for ghost in ghosts_group:
            ghost.kill()

    # Estados do Jogo
    TELA_INICIAL = "TELA_INICIAL"
    JOGANDO = "JOGANDO"
    GAME_OVER = "GAME_OVER"
    game_state = TELA_INICIAL

    # eventos
    GHOST_SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(GHOST_SPAWN_EVENT, 2000)  # spawn de fantasmas a cada 2 segundos

    # posicao do life count
    POSICAO_X_LIFE_COUNT = 50
    POSICAO_Y_LIFE_COUNT = 50

    # adiciona as sprites
    player = Player()
    ghosts = pygame.sprite.Group()

    # clock para controlar o framerate
    clock = pygame.time.Clock()
    
    running = True
    while running:
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
                    if event.key == pygame.K_RETURN: # Reiniciar
                        inicializa_jogo(player, ghosts)
                        game_state = JOGANDO
                    elif event.key == pygame.K_ESCAPE: # Sair
                        running = False

        # logica e desenho baseados no estado do jogo
        if game_state == TELA_INICIAL:
            screen.blit(scaled_initial_background, initial_background_rect) 
            instrucao_surface = font_instruction.render("Pressione ENTER para começar", True, (38, 56, 48))

            instrucao_rect = instrucao_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            screen.blit(instrucao_surface, instrucao_rect)

        elif game_state == JOGANDO:
            # coloca o background na tela
            screen.blit(scaled_background, background_rect)
            # atualiza e desenha o grupo de sprites
            player.update()
            player.draw(screen)
            pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2) # desenha hitbox no personagem

            for ghost in ghosts:
                ghost.update()
                ghost.draw(screen)
            # coloca a vida atual do personagem
            screen.blit(player.life_count_atual, (POSICAO_X_LIFE_COUNT, POSICAO_Y_LIFE_COUNT))

            # Condição de Game Over
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

        
        # atualiza a tela
        pygame.display.flip()

        # define o FPS da screen
        clock.tick(FPS)
        
    pygame.quit()
