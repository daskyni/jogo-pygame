import pygame
from main import SCREEN_WIDTH, SCREEN_HEIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # variaveis que definem o numero de sprites
        self.first_sprite_number = 0
        self.last_sprite_number = 7

        # fator de escala para a sprite do personagem
        self.scale_factor = 2

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

    # metodo que atualiza a direção do movimento e animação
    def update(self):
        if self.walking:
            self.animate_walk()
        else:
            # se não estiver andando, mostra o primeiro frame na direção correta
            self.image = self.walk_frames[0]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

        # atualiza a posição do jogador
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed

        # LOGICA DE COLISAO COM O MAPA - impedir que o personagem saia do mapa

        # colisao com a borda direita do mapa
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
