import pygame
from ghosts import Ghost
from player import Player, PLAYER_MELEE_RANGE
from projectile import Projectile
import random

# define o FPS do jogo
FPS = 60

# define o tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

GHOST_SPAWN_POINTS = [
    (SCREEN_WIDTH // 2, 0),               # meio do topo
    (SCREEN_WIDTH // 2, SCREEN_HEIGHT),   # meio da base
    (0, SCREEN_HEIGHT // 2),               # meio da esquerda
    (SCREEN_WIDTH, SCREEN_HEIGHT // 2)    # meio da direita
]

def load_smoke_frames():
    frames = []
    for i in range(0, 10):
        img = pygame.image.load(f'./sprites/personagens/ceifador/fumaca/fumaca_{i}.png').convert_alpha()
        frames.append(img)
    return frames

def load_digit_sprites(target_size=None):
    digits = []
    for i in range(10):
        img = pygame.image.load(f'./sprites/tela/numeros/contador_{i}.png').convert_alpha()
        if target_size:
            img = pygame.transform.scale(img, target_size)
        digits.append(img)
    return digits


def draw_number(surface, number, pos, digit_sprites, spacing):
    str_num = str(number)
    x, y = pos
    for char in str_num:
        digit = int(char)
        digit_img = digit_sprites[digit]
        surface.blit(digit_img, (x, y))
        x += digit_img.get_width() - spacing

def inicializa_jogo(player, ghosts):
    player.lives_remaining = player.total_lives
    player.walking = False
    player.is_attacking = False
    player.direction_x = 0
    player.direction_y = 0
    player.invulnerable = False
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    for ghost in ghosts:
        ghost.kill()
    global ghosts_killed
    ghosts_killed = 0

ghosts_killed = 0

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()  # Inicializa o mixer de som

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

    game_over_background_path = "./background/GAME OVER.png"
    game_over_background_image = pygame.image.load(game_over_background_path).convert()
    scaled_game_over_background = pygame.transform.scale(game_over_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over_background_rect = scaled_game_over_background.get_rect()


    FONT_PATH = "./fonts/PressStart2P.ttf"
    pygame.font.init()
    try:
        font_stats = pygame.font.Font(FONT_PATH, 18)
        font_title = pygame.font.Font(FONT_PATH, 18)
        font_instruction = pygame.font.Font(FONT_PATH, 18)
    except pygame.error:
        print(f"Aviso: Fonte '{FONT_PATH}' não encontrada. Usando fonte padrão.")
        font_stats = pygame.font.Font(None, 38)
        font_title = pygame.font.Font(None, 76)
        font_instruction = pygame.font.Font(None, 42)

    # Carrega o som de ataque
    scythe_swoosh_sound = None
    projectile_launch_sound = None
    try:
        scythe_swoosh_sound = pygame.mixer.Sound('./sounds/foice.wav') # Som da foice
        projectile_launch_sound = pygame.mixer.Sound('./sounds/projetil.wav') # Som do lançamento do projétil
    except pygame.error:
        print("Aviso: Arquivo de som para foice ou projétil não encontrado. Sons de ataque não serão reproduzidos.")
        scythe_swoosh_sound = None
        projectile_launch_sound = None

    TELA_INICIAL = "TELA_INICIAL"
    JOGANDO = "JOGANDO"
    GAME_OVER = "GAME_OVER"
    game_state = TELA_INICIAL

    # Menu interativo
    menu_options = ["Iniciar jogo", "Sair"]
    selected_option = 0

    game_over_options = ["Reiniciar", "Sair"]
    game_over_selected = 0


    GHOST_SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(GHOST_SPAWN_EVENT, 2000)

    icon_vida = pygame.image.load('./sprites/tela/contador_vida.png').convert_alpha()
    icon_ghost = pygame.image.load('./sprites/tela/contador_fantasmas.png').convert_alpha()

    icon_size = (70, 45)
    icon_vida = pygame.transform.scale(icon_vida, icon_size)
    icon_ghost = pygame.transform.scale(icon_ghost, icon_size)

    POS_ICON_VIDA = (20, 70)
    POS_NUM_VIDA = (POS_ICON_VIDA[0] + icon_size[0] + 5, POS_ICON_VIDA[1])

    POS_ICON_GHOST = (20, 20)
    POS_NUM_GHOST = (POS_ICON_GHOST[0] + icon_size[0] + 5, POS_ICON_GHOST[1])

    digit_height = 40  
    temp_img = pygame.image.load('./sprites/tela/numeros/contador_0.png').convert_alpha()
    aspect_ratio = temp_img.get_width() / temp_img.get_height()
    digit_width = int(digit_height * aspect_ratio)

    digit_target_size = (digit_width, digit_height)
    digit_sprites = load_digit_sprites(digit_target_size)

    player = Player()
    ghosts = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    smoke_frames = load_smoke_frames()

    clock = pygame.time.Clock()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == GHOST_SPAWN_EVENT:
                new_ghost = Ghost(player, ghosts, spawn_pos=random.choice(GHOST_SPAWN_POINTS))
                ghosts.add(new_ghost)

            if game_state == TELA_INICIAL:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Iniciar jogo":
                            inicializa_jogo(player, ghosts)
                            game_state = JOGANDO
                        elif menu_options[selected_option] == "Sair":
                            running = False

            elif game_state == JOGANDO:
                player.handle_input(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Tenta iniciar o ataque. Se for bem-sucedido (não em cooldown)...
                        if player.attack(scythe_swoosh_sound):
                            # Verifica se foi um ataque corpo a corpo (melee)
                            melee_hit_occurred = False
                            for ghost in ghosts:
                                distance = pygame.Vector2(player.rect.center).distance_to(ghost.rect.center)
                                if distance <= PLAYER_MELEE_RANGE:
                                    ghost.take_damage(player.player_damage)
                                    melee_hit_occurred = True
                            
                            # Se NENHUM fantasma foi atingido no corpo a corpo, lança o projétil
                            if not melee_hit_occurred:
                                if projectile_launch_sound:
                                    projectile_launch_sound.play()
                                # Calcula a posição inicial do projétil com um deslocamento
                                offset_distance = 40
                                proj_start_pos = pygame.Vector2(player.rect.center) + player.direction * offset_distance
                                # Cria o projétil usando o vetor de direção do jogador
                                proj = Projectile(proj_start_pos, player.direction, smoke_frames)
                                projectiles.add(proj)

            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game_over_selected = (game_over_selected - 1) % len(game_over_options)
                    elif event.key == pygame.K_DOWN:
                        game_over_selected = (game_over_selected + 1) % len(game_over_options)
                    elif event.key == pygame.K_RETURN:
                        if game_over_options[game_over_selected] == "Reiniciar":
                            inicializa_jogo(player, ghosts)
                            game_state = JOGANDO
                        elif game_over_options[game_over_selected] == "Sair":
                            running = False


        if game_state == JOGANDO:
            projectiles.update()

            # Colisão projetil x fantasmas
            for proj in projectiles:
                hits = [ghost for ghost in ghosts if ghost.rect.colliderect(proj.hitbox)]
                if hits:
                    for ghost in hits:
                        ghost.take_damage(1)
                        if ghost.lives_remaining <= 0:
                            ghosts_killed += 1
                    proj.kill()

        # Desenha telas
        if game_state == TELA_INICIAL:
            screen.blit(scaled_initial_background, initial_background_rect)
            menu_y_start = 340
            for i, option in enumerate(menu_options):
                color = (102, 137, 119) if i == selected_option else (102, 137, 119)
                prefix = "→ " if i == selected_option else "   "
                option_surface = font_instruction.render(prefix + option, True, color)
                option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_y_start + i * 40))
                screen.blit(option_surface, option_rect)

        elif game_state == JOGANDO:
            screen.blit(scaled_background, background_rect)

            for ghost in ghosts:
                ghost.update()
                ghost.draw(screen)

            player.update()
            player.draw(screen)

            projectiles.draw(screen)

            screen.blit(icon_ghost, POS_ICON_GHOST)
            draw_number(screen, ghosts_killed, POS_NUM_GHOST, digit_sprites, 2)

            screen.blit(icon_vida, POS_ICON_VIDA)
            draw_number(screen, player.lives_remaining, POS_NUM_VIDA, digit_sprites, 2)

            if player.lives_remaining <= 0:
                game_state = GAME_OVER

        elif game_state == GAME_OVER:
            screen.blit(scaled_game_over_background, game_over_background_rect)

            # Texto de fantasmas mortos
            kill_count_text = f"Você matou {ghosts_killed} fantasmas"
            kill_count_surface = font_stats.render(kill_count_text, True, (102, 137, 119))
            kill_count_rect = kill_count_surface.get_rect(center=(SCREEN_WIDTH // 2, 300))
            screen.blit(kill_count_surface, kill_count_rect)

            # Menu com flechinha
            menu_y_start = 340
            for i, option in enumerate(game_over_options):
                color = (102, 137, 119)
                prefix = "→ " if i == game_over_selected else "   "
                option_surface = font_instruction.render(prefix + option, True, color)
                option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_y_start + i * 40))
                screen.blit(option_surface, option_rect)


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
