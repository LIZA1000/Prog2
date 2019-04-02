import os
import sys
import pygame

FPS = 50
WIDTH = 800  # высота и ширина поля
HEIGHT = 600
HIGH = 20  # максимальное количество ударов шара о стенки поля


def load_image(name, color_key=None):  # функция отвечает за загрузку картинки
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key != None:
        image.set_colorkey(color_key)
    image = image.convert_alpha()

    if color_key is not None:  # добавление прозрачности изображению при необходимости
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):  # функция отвечает за загрузку уровня и его подготовку для считывания
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):    #считывание и генерация уровня
    new_player, x, y = None, None, None    #заготовка для спрайта-шара
    for y in range(len(level)):
        for x in range(len(level[y])):    #считываем фйайл с уровнем, перемещаясь по каждому символу
            if level[y][x] == '#':
                if (x != 15 and level[y][x + 1] == '#') or (x != 0 and level[y][x - 1] == '#'):
                    #блок считаем горизонтальным, если по бокам у него есть "соседи"
                    Tile('wall', x, y, 'horisontal')
                elif (y != 11 and level[y + 1][x] == '#') or (y != 0 and level[y - 1][x] == '#'):
                    #блок считаем вертикальным, если сверху и снизу от него есть "соседи"
                    Tile('wall', x, y, 'vertical')
            elif level[y][x] == '*':   #специальный символ для чёрной дыры
                Tile('hole', x, y, '')
            elif level[y][x] == '@':   #и для самого игрока
                new_player = Player(x, y)
            elif level[y][x] == 'R':   #и для кнопки "Начать заново"(перезапуск)
                Tile('restart', x, y, 'r')
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def start_screen():  # стартовый экран
    fon = pygame.transform.scale(load_image('begin.jpg'), (WIDTH, HEIGHT))   #стартовая картинка
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # переход дальше
        pygame.display.flip()
        clock.tick(FPS)


def instructions():  # экран с инструкцией, идёт после стартового экрана
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

    fon = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))    #другая фоновая картинка
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 35)    #размер шрифта
    text_coord = 30    #отступ текста сверху
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('orchid3'))    #цвет текста
        intro_rect = string_rendered.get_rect()
        text_coord += 10    #расстояние между строками
        intro_rect.top = text_coord
        intro_rect.x = 10    #отступ текста слева
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


def terminate():    #функция выхода из игры
    pygame.quit()
    sys.exit()


class Tile(pygame.sprite.Sprite):   #класс блоков-препятствий, чёрной дыры и кнопки перезапуска
    def __init__(self, tile_type, pos_x, pos_y, place):
        super().__init__(tiles_group, all_sprites)
        if place == 'horisontal':
            self.add(horisontal_block)
        elif place == 'vertical':
            self.add(vertical_block)
        elif place == '':
            self.add(black_hole)
        elif place == 'r':
            self.add(Restart)
        self.image = tile_images[tile_type]    #подгрузка картинок к спрайтам
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):    #главный спрайт-шар
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.add(sprite)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):    #движение и столкновение спрайта
        global VX    #его собственная скорость
        global VY
        global WX    #скорость панелей выигрыша и проигрыша
        global WY
        global WX2
        global WY2
        global hits    #удары шара о стенки
        self.rect = self.rect.move(VX, VY)
        if pygame.sprite.spritecollideany(self, horisontal_block):
            #проверка столкновения с горизонтальной стеной из блоков
            VY = -VY
            hits += 1
            if hits == HIGH:   #и проверка на количество столкновений
                hits = 0
                self.kill()
                WX2 = 7    #вызов панели проигрыша
        if pygame.sprite.spritecollideany(self, vertical_block):
            #проверка столкновения с вертикальной стеной из блоков
            VX = -VX
            hits += 1
            if hits == HIGH:    #и проверка на количество столкновений
                hits = 0
                self.kill()
                WX2 = 7    #вызов панели проигрыша
        if pygame.sprite.spritecollideany(self, black_hole):
            #проверка касания чёрной дыры
            VX = 0
            VY = 0
            WX = 7    #вызов панели выигрыша
            self.kill()


class winner(pygame.sprite.Sprite):    #панель выигрыша
    def __init__(self, radius, x, y):
        super().__init__(all_sprites)
        self.add(sprite)
        self.radius = radius
        self.image = load_image('winner.jpg')   #картинка панели
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = pygame.Rect(x, y, radius, radius)

    def update(self):    #движение панели
        global WX
        global WY
        self.rect = self.rect.move(WX, WY)


class looser(pygame.sprite.Sprite):    #панель проигрыша
    def __init__(self, radius, x, y):
        super().__init__(all_sprites)
        self.add(sprite)
        self.radius = radius
        self.image = load_image('looser.jpg')    #картинка панели
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = pygame.Rect(x, y, radius, radius)

    def update(self):    #движение панели
        global WX2
        global WY2
        self.rect = self.rect.move(WX2, WY2)


pygame.init()
pygame.key.set_repeat(200, 70)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

start_screen()    #начало игры
instructions()    #экран с инструкцией

#изображения к спрайтам
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


def main_play():    #главная функция игры
    global board
    global Background
    global running
    global helper
    global winner
    global looser
    global VX
    global VY
    global WX
    global WY
    global WX2
    global WY2
    global hits
    global player
    global all_sprites
    global tiles_group
    global vertical_block
    global horisontal_block
    global Restart
    global black_hole
    global player_group
    global sprite

    VX = 0  # сначала скорость шара по x и по y равна 0
    VY = 0
    WX = 0  # это скорость таблички "Вы выиграли" сначала
    WY = 0
    WX2 = 0  # а это - таблички "Игра окончена"
    WY2 = 0

    hits = 0
    player = None
    #определение всех спрайтовых групп
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    vertical_block = pygame.sprite.Group()
    horisontal_block = pygame.sprite.Group()
    Restart = pygame.sprite.Group()
    black_hole = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    sprite = pygame.sprite.Group()

    board = [[0] * WIDTH for _ in range(HEIGHT)]   #создание поля
    player, level_x, level_y = generate_level(load_level("level1.txt"))   #создание уровня
    Background = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))   #фон

    running = True    #начинаем игру
    helper = False   #эта переменная поможет отследить, был ли уже совершён клик мышкой
    #до следующего клика
    #это нужно для того, чтобы спрайт не менял траекторию уже начатого движения
    #к следующему клику мышкой
    winner(0, -WIDTH, 0)    #тут находятся панели выигрпыша и проигрыша
    looser(0, -WIDTH, 0)

    while running:    #обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #выход из игры
                running = False
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:    #клик мышкой
                pos = pygame.mouse.get_pos()    #позиция мыши
                #отслеживаем "кликнутые" спрайты
                clicked_sprites = [s for s in Restart if s.rect.collidepoint(pos)]
                if len(clicked_sprites) != 0:
                    #там может находиться только кнопка перезапуска
                    #поэтому кликнули на неё
                    #и мы перезапускаем игру
                    return
                else:
                    if not helper:   #если мышкой пока не кликали
                        #отслеживаем позицию клика и направляем туда спрайт-шар
                        VX = (event.pos[0] - player.rect.x) // 15
                        #деление на 15 нужно для разумного значения скорости шара
                        VY = (event.pos[1] - player.rect.y) // 15
                        helper = True    #тогда клик уже был совершён
        screen.fill(pygame.Color(0, 0, 0))
        screen.blit(Background, (0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


while True:    #это нужно для перезапуска игры
    main_play()
terminate()
