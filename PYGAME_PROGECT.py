import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 800
HEIGHT = 600
STEP = 10

VX = 0
VY = 0
WX = 0
WY = 0
WX2 = 0
WY2 = 0
HITS = 0
HIGH = 15

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
vertical_block = pygame.sprite.Group()
horisontal_block = pygame.sprite.Group()
Restart = pygame.sprite.Group()
black_hole = pygame.sprite.Group()
player_group = pygame.sprite.Group()
sprite = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key != None:
        image.set_colorkey(color_key)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    res, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                if (x != 15 and level[y][x + 1] == '#') or (x != 0 and level[y][x - 1] == '#'):
                    Tile('wall', x, y, 'horisontal')
                elif (y != 11 and level[y + 1][x] == '#') or (y != 0 and level[y - 1][x] == '#'):
                    Tile('wall', x, y, 'vertical')
            elif level[y][x] == '*':
                Tile('hole', x, y, '')
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == 'R':
                Tile('restart', x, y, 'r')
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('begin.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def instructions():
    intro_text = ['                                   << I N S T R U C T I O N >>',
                  '',
                  '',
                  '',
                  '               Click mouse to make the fireball go to the cursor.',
                  '                             Click on return button to return.',
                  'If the fireball touches the black hole before it strikes walls 15 times,',
                  '                                            YOU WILL WIN!',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '                                             click to BEGIN']

    fon = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 35)
    text_coord = 30
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('orchid3'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


wall = load_image('box.png')
wall = pygame.transform.scale(wall, (50, 50))
hole_image = load_image('hole.png')
hole_image = pygame.transform.scale(hole_image, (100, 100))
res_pic = load_image('restart.png')
res_pic = pygame.transform.scale(res_pic, (100, 100))
tile_images = {'wall': wall, 'hole': hole_image, 'restart': res_pic}
player_image = load_image('star.png')
player_image = pygame.transform.scale(player_image, (44, 44))
tile_width = tile_height = 50
m_width = m_height = 10


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, place):
        super().__init__(tiles_group, all_sprites)
        if place == 'horisontal':
            self.add(horisontal_block)
        elif place == 'vertical':
            self.add(vertical_block)
        elif place == '':
            self.add(black_hole)
        elif place == 'R':
            self.add(Restart)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.add(sprite)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        global VX
        global VY
        global WX
        global WY
        global WX2
        global WY2
        global HITS
        self.rect = self.rect.move(VX, VY)
        if pygame.sprite.spritecollideany(self, horisontal_block):
            VY = -VY
            HITS += 1
            if HITS == HIGH:
                HITS = 0
                self.kill()
                WX2 = 7
        if pygame.sprite.spritecollideany(self, vertical_block):
            VX = -VX
            HITS += 1
            if HITS == HIGH:
                HITS = 0
                self.kill()
                WX2 = 7
        if pygame.sprite.spritecollideany(self, black_hole):
            VX = 0
            VY = 0
            WX = 7
            self.kill()


class winner(pygame.sprite.Sprite):
    def __init__(self, radius, x, y):
        super().__init__(all_sprites)
        self.add(sprite)
        self.radius = radius
        self.image = load_image('winner.jpg')
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = pygame.Rect(x, y, radius, radius)

    def update(self):
        global WX
        global WY
        self.rect = self.rect.move(WX, WY)


class looser(pygame.sprite.Sprite):
    def __init__(self, radius, x, y):
        super().__init__(all_sprites)
        self.add(sprite)
        self.radius = radius
        self.image = load_image('looser.jpg')
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = pygame.Rect(x, y, radius, radius)

    def update(self):
        global WX2
        global WY2
        self.rect = self.rect.move(WX2, WY2)


start_screen()
instructions()


def main_play():
    global board
    global Background
    global running
    global helper
    global winner
    global looser
    global VX
    global VY

    board = [[0] * WIDTH for _ in range(HEIGHT)]
    player, level_x, level_y = generate_level(load_level("level1.txt"))
    Background = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))

    running = True
    helper = False
    winner(0, -WIDTH, 0)
    looser(0, -WIDTH, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not helper:
                    VX = (event.pos[0] - player.rect.x) // 15
                    VY = (event.pos[1] - player.rect.y) // 15
                    helper = True
                else:
                    pos = pygame.mouse.get_pos()
                    clicked_sprites = []
                    print('1')
                    clicked_sprites = [s for s in Restart if s.rect.collidepoint(pos)]
                    print('2')
                    if len(clicked_sprites) != 0:
                        print('3')
                        return

        screen.fill(pygame.Color(0, 0, 0))
        screen.blit(Background, (0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


while True:
    main_play()
terminate()
