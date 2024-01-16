import pygame
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

tile_size = 55
cols = 12
margin = 100
width = 660
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Level Editor')

sky_image = pygame.image.load('img/8Sky.png')
hills_image = pygame.image.load('img/7Hills.png')
forest_image = pygame.image.load('img/6Forest.png')
bushes_image = pygame.image.load('img/5BackBushes.png')
ground_image = pygame.image.load('img/4Ground.png')
grass_image = pygame.image.load('img/grass.png')
hedg_image = pygame.image.load('img/hedg1.png')
bush_image = pygame.image.load('img/Bush.png')
coin_img = pygame.image.load('img/crystal.png')

exit_img = pygame.image.load('img/exit_door.png')
save_img = pygame.image.load('img/saveLevel.png')
load_img = pygame.image.load('img/loadLevel.png')

clicked = False
level = 1

white = (255, 255, 255)
black = (0, 0, 0)

font = pygame.font.SysFont('Pixel Digivolve Cyrillic', 10)

world_data = []
for row in range(12):
    r = [0] * 12
    world_data.append(r)

for tile in range(0, 12):
    world_data[11][tile] = 1
    world_data[0][tile] = 0
    world_data[tile][0] = 1
    world_data[tile][11] = 1


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_grid():
    for c in range(21):
        pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, height - margin))
        pygame.draw.line(screen, white, (0, c * tile_size), (width, c * tile_size))


def draw_world():
    for row in range(12):
        for col in range(12):
            if world_data[row][col] > 0:
                if world_data[row][col] == 1:
                    # земля
                    img = pygame.transform.scale(grass_image, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 2:
                    # ежи
                    img = pygame.transform.scale(hedg_image, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 3:
                    # кусты
                    img = pygame.transform.scale(bush_image, (65, 58))
                    screen.blit(img, (col * tile_size, row * tile_size))

                if world_data[row][col] == 4:
                    # выход
                    img = pygame.transform.scale(exit_img, (55, 100))
                    screen.blit(img, (col * tile_size, row * tile_size - 45))
                if world_data[row][col] == 5:
                    # монетки
                    img = pygame.transform.scale(coin_img, (32, 32))
                    screen.blit(img, (col * tile_size + 10, row * tile_size + 30))


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


save_button = Button(500, 670, save_img)
load_button = Button(350, 670, load_img)

run = True
while run:

    clock.tick(fps)

    screen.fill(black)
    screen.blit(sky_image, (0, 0))
    screen.blit(hills_image, (0, 0))
    screen.blit(forest_image, (0, 0))
    screen.blit(bushes_image, (0, 0))
    screen.blit(ground_image, (0, 0))

    draw_grid()
    draw_world()

    if save_button.draw():
        # сохранение или загрузка уровней
        pickle_out = open(f'level{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
    if load_button.draw():
        if path.exists(f'level{level}_data'):
            pickle_in = open(f'level{level}_data', 'rb')
            world_data = pickle.load(pickle_in)

    draw_text(f'Уровень: {level}', font, white, tile_size - 30, height - 60)
    draw_text('Нажмите вверх или вниз чтобы сменить уровень', font, white, tile_size - 30, height - 40)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
            pos = pygame.mouse.get_pos()
            x = pos[0] // tile_size
            y = pos[1] // tile_size
            if x < 12 and y < 12:
                if pygame.mouse.get_pressed()[0] == 1:
                    world_data[y][x] += 1
                    if world_data[y][x] > 5:
                        world_data[y][x] = 0
                elif pygame.mouse.get_pressed()[2] == 1:
                    world_data[y][x] -= 1
                    if world_data[y][x] < 0:
                        world_data[y][x] = 5
        if event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            elif event.key == pygame.K_DOWN and level > 1:
                level -= 1

    pygame.display.update()

pygame.quit()
