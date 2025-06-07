import pygame

# define o FPS do jogo
FPS = 60

# define o tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

PLAYER_ATTACK_DAMAGE = 35 # Dano que o player causa aos fantasmas

if __name__ == "__main__":
    
    from ghosts import Ghost # Movido para dentro do if __name__
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

    # Estados do Jogo
    TELA_INICIAL = "TELA_INICIAL"
    JOGANDO = "JOGANDO"
    GAME_OVER = "GAME_OVER"
    game_state = TELA_INICIAL

    # Função para (re)inicializar o mundo do jogo (jogador e fantasmas)
    def inicializar_mundo_jogo(p_obj, all_s_group, g_s_group, g_imgs_list, num_fantasmas=3):
        p_obj.health = p_obj.max_health
        p_obj.xp = 0
        p_obj.level = 1
        p_obj.xp_to_next_level = p_obj.base_xp_to_next_level
        p_obj.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        p_obj.invulnerable = False
        p_obj.is_attacking = False
        p_obj.direction_x = 0
        p_obj.direction_y = 0
        p_obj.walking = False

        for fantasma_existente in g_s_group:
            fantasma_existente.kill() # Remove dos grupos all_s_group e g_s_group

        for _ in range(num_fantasmas):
            novo_fantasma = Ghost(p_obj, g_imgs_list, g_s_group) # Passa o grupo de fantasmas
            all_s_group.add(novo_fantasma)
            g_s_group.add(novo_fantasma)

    ghost_images = []
    for i in range(0, 3):
        img = pygame.image.load(f"./sprites/personagens/fantasma/flutuando/fantasma_flutuando_{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        ghost_images.append(img)

    # adiciona as sprites
    player = Player()
    all_sprites = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    
    # Adiciona o jogador ao grupo principal de sprites (apenas uma vez)
    all_sprites.add(player) 

    # clock para controlar o framerate
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == TELA_INICIAL:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        inicializar_mundo_jogo(player, all_sprites, ghosts, ghost_images, 3)
                        game_state = JOGANDO
            elif game_state == JOGANDO:
                player.handle_input(event)
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Reiniciar
                        inicializar_mundo_jogo(player, all_sprites, ghosts, ghost_images, 3)
                        game_state = JOGANDO
                    elif event.key == pygame.K_ESCAPE: # Sair
                        running = False

        # Lógica e Desenho baseados no estado do jogo
        if game_state == TELA_INICIAL:
            # screen.fill((20, 20, 50)) # Fundo azul escuro - Removido
            screen.blit(scaled_initial_background, initial_background_rect) 
            instrucao_surface = font_instruction.render("Pressione ENTER para começar", True, (38, 56, 48))

            instrucao_rect = instrucao_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            screen.blit(instrucao_surface, instrucao_rect)

        elif game_state == JOGANDO:
            # coloca o background na tela
            screen.blit(scaled_background, background_rect)

            # atualiza e desenha o grupo de sprites
            all_sprites.update()
            all_sprites.draw(screen)

            # Lógica de ataque do Player
            if player.is_attacking:
                ghosts_hit_by_player = pygame.sprite.spritecollide(player, ghosts, False, pygame.sprite.collide_rect)
                for ghost_hit in ghosts_hit_by_player:
                    if not ghost_hit.invulnerable:
                        ghost_hit.take_damage(PLAYER_ATTACK_DAMAGE)

            # Exibir HP do Player
            hp_text = font_stats.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
            screen.blit(hp_text, (10, 10))

            # Exibir Nível e XP do Player
            level_text = font_stats.render(f"Level: {player.level}", True, (255, 255, 255))
            screen.blit(level_text, (10, 40))
            xp_text = font_stats.render(f"XP: {player.xp}/{player.xp_to_next_level}", True, (255, 255, 255))
            screen.blit(xp_text, (10, 70))

            # Desenhar barras de vida dos fantasmas
            for ghost in ghosts:
                ghost.draw_health_bar(screen)

            # Condição de Game Over
            if player.health <= 0:
                game_state = GAME_OVER
        
        elif game_state == GAME_OVER:
            # screen.fill((50, 20, 20)) # Fundo vermelho escuro - Removido
            screen.blit(scaled_initial_background, initial_background_rect) # Novo fundo
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
