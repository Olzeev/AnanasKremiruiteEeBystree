import pygame
from vis_const import *
from math import sin, cos, radians
from random import randint, random
import requests
import time
from FighterAnt import *
from ScoutAnt import *

from algorithm import *

pygame.init()

sc = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def draw_hex(x, y, edge_size, bg_color, outline_color):
    points = [(x + edge_size * cos(radians(30 + i * 60)), y + edge_size * sin(radians(30 + i * 60))) for i in range(6)]
    pygame.draw.polygon(sc, bg_color, points)
    pygame.draw.polygon(sc, outline_color, points, 2)

def print_text(text, pos, size, color, align='left'):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    x, y = pos

    if align == 'center':
        x -= surf.get_width() / 2
    elif align == 'right':
        x -= surf.get_width()

    sc.blit(surf, (x, y - surf.get_height() / 2))


def check_in_window(x, y):
    return x >= 0 and x <= WIDTH and y >= 0 and y <= HEIGHT


def hex_to_dec(q, r):
    x = xc + q * gap + (r % 2) * gap / 2
    y = yc + r * gap * cos(radians(30))
    return (x, y)


class Food:
    def __init__(self, type1, amount):
        self.type = type1
        self.amount = amount

class FoodOnMap:
    def __init__(self, type1, q, r, amount):
        self.type = type1
        self.q = q
        self.r = r
        self.amount = amount

    def draw(self):
        x, y = hex_to_dec(self.q, self.r)
        draw_hex(x, y, edge_size_scaled, HEX_FOOD_BG_COLOR, HEX_FOOD_OUTLINE_COLOR)
        
        print_text(['Я', "Х", "Н"][self.type - 1], (x - gap / 10, y), int(gap * 0.8), (50, 50, 255), 'right')
        print_text(str(self.amount), (x, y), int(gap * 0.8), (50, 50, 255), 'left')


class Ant:
    def __init__(self, id1, type1, q, r, health, food, lastMove, move, lastAttack, lastEnemyAnt):
        self.id = id1
        self.type = type1
        self.q, self.r = q, r
        self.health = health
        self.food = food
        self.lastMove = lastMove
        self.move = move
        self.lastAttack = lastAttack
        self.lastEnemyAnt = lastEnemyAnt
        a = [1, 1, 4]
        self.pov = a[type1]
        self.speed = [30, 70, 20][self.type]

    def draw(self):
        x, y = hex_to_dec(self.q, self.r)
        draw_hex(x, y, edge_size_scaled, HEX_VISIBLE_BG_COLOR, HEX_VISIBLE_OUTLINE_COLOR)
        print_text(['Раб', "Б", "Раз"][self.type], (x, y - gap * 0.1), int(gap * 0.7), (0, 0, 0), 'center')
        print_text(str(self.health), (x, y + gap / 4), int(gap * 0.4), (255, 0, 0), 'center')
        if self.food is None:
            print_text(['Я', "Х", "Н"][self.food.type - 1], (x - gap / 10, y + gap / 2), int(gap * 0.4), (50, 50, 255),'right' )
            print_text(str(self.food.amount), (x + gap / 10, y + gap / 2), int(gap * 0.4), (50, 50, 255), 'left')


class Enemy:
    def __init__(self, type1, q, r, health, food, attack):
        self.type = type1
        self.q = q
        self.r = r
        self.health = health
        self.food = food
        self.attack = attack

    def draw(self):
        x, y = hex_to_dec(self.q, self.r)
        draw_hex(x, y, edge_size_scaled, HEX_ENEMY_BG_COLOR, HEX_ENEMY_OUTLINE_COLOR)

        print_text(['Раб', "Б", "Раз"][enemy.type], (x, y - gap * 0.1), int(gap * 0.7), (0, 0, 0), 'center')
        print_text(str(enemy.health), (x, y + gap / 4), int(gap * 0.4), (255, 0, 0), 'center')
        if self.food is not None:
            print_text(['Я', "Х", "Н"][enemy.food.type - 1], (x - gap / 10, y + gap / 2), int(gap * 0.4), (50, 50, 255),'right' )
            print_text(str(enemy.food.amount), (x + gap / 10, y + gap / 2), int(gap * 0.4), (50, 50, 255), 'left')
        
class Hex:
    def __init__(self, type1, q, r, cost):
        self.type = type1
        self.q = q
        self.r = r
        self.cost = cost

    def draw(self):
        x, y = hex_to_dec(self.q, self.r)
        draw_hex(x, y, edge_size_scaled, HEX_BG_COLOR[self.type - 1], HEX_OUTLINE_COLOR[self.type - 1])


scale_k = 1
xc, yc = WIDTH / 2, HEIGHT / 2
dragging = False
last_mouse_pos = (0, 0)
prev_time = 0
frame_count = 0

raiding_time = False
but1 = pygame.transform.scale(pygame.image.load('media/image1.png'), (100, 100))
but2 = pygame.transform.scale(pygame.image.load('media/image2.png'), (100, 100))


def parse():
    r = requests.get(
        url="https://games-test.datsteam.dev/api/arena",
        json={},
        headers={"X-Auth-Token": "3c541e6b-fcbf-427e-91a0-6e261e425a60"},
    )

    global home, spot, hexes, ants, enemies, foods
    res = r.json()
    print(res)
    ants_r = res['ants']
    ants = []
    for ant in ants_r:
        ants.append(Ant(ant['id'], ant['type'], ant['q'], ant['r'], ant['health'], Food(ant['food']['type'], ant['food']['amount']), None, None, None, None))

    enemies_r = res['enemies']
    enemies = []

    for enemy in enemies_r:
        enemies.append(Enemy(enemy['type'], enemy['q'], enemy['r'], enemy['health'], Food(enemy['food']['type'], enemy['food']['amount']), enemy['attack']))

    foods_r = res['food']
    foods = []
    for food in foods_r:
        foods.append(FoodOnMap(food['type'], food['q'], food['r'], food['amount']))

    
    home = res['home']
    spot = res['spot']
    hexes = [Hex(h['type'], h['q'], h['r'], h['cost']) for h in res['map']]

    general_map.update(ants, enemies, foods, hexes, home)

    for el in ants:
        if el.type == 0:
            if el.id not in list(map(lambda x: x.id, worker_ants)):
                worker_ants.append(WorkerAnt(el.id, el.health, (el.q, el.r), 30))
        elif el.type == 1:
            if el.id not in list(map(lambda x: x.id, fighter_ants)):
                #fighter_ants.append(FighterAnt(el.id, el.health, (el.q, el.r), 70))
                pass
        elif el.type == 2:
            if el.id not in list(map(lambda x: x.id, scout_ants)):
                scout_ants.append(ScoutAnt(el.id, el.health, (el.q, el.r)))

    for el in worker_ants:
        t = None
        for el1 in ants:
            if el1.id == el.id:
                t = el1
                break
        
        if t is None:
            worker_ants.remove(el)
        else:
            el.update(t.health, (t.q, t.r))

    for el in fighter_ants:
        t = None
        for el1 in ants:
            if el1.id == el.id:
                t = el1
                break
        
        if t is None:
            fighter_ants.remove(el)
        else:
            el.update(t.health, (t.q, t.r))
            
    for el in scout_ants:
        t = None
        for el1 in ants:
            if el1.id == el.id:
                t = el1
                break
        
        if t is None:
            scout_ants.remove(el)
        else:
            el.update(t.health, (t.q, t.r))
            
            
    
map_size = 200
ants = [Ant(i, randint(0, 2), randint(0, map_size - 1), randint(0, map_size - 1), 100, Food(randint(0, 2), randint(1, 10)), None, None, None, None) for i in range(20)]
enemies = [Enemy(randint(0, 2), randint(0, map_size - 1), randint(0, map_size - 1), 100, Food(randint(0, 2), randint(1, 10)), 20) for i in range(10)]
foods = [FoodOnMap(randint(0, 2), randint(0, map_size - 1), randint(0, map_size - 1), randint(1, 10)) for i in range(50)]
home = [{'q': 20, 'r': 20}, {'q': 20, 'r': 21}, {'q': 21, 'r': 20}]
spot = {'q': 20, 'r': 20}
hexes = [Hex(randint(1, 4), randint(0, 200), randint(0, 200), 1)]


general_map = Map([[[] for i in range(MAP_WIDTH)] for j in range(MAP_HEIGHT)])
worker_ants = []
scout_ants = []
fighter_ants = []
all_ants = []



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            old_scale = scale_k
            scale_k += event.y * 0.1 
            scale_k = max(0.01, min(scale_k, 10.0))  
            
            xc = mouse_x - (mouse_x - xc) * (scale_k / old_scale)
            yc = mouse_y - (mouse_y - yc) * (scale_k / old_scale)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[0] <= 100 and pos[1] <= 100:
                raiding_time = not raiding_time
            else:
                if event.button == 1: 
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        if event.type == pygame.MOUSEMOTION and dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - last_mouse_pos[0]
            dy = mouse_y - last_mouse_pos[1]
            xc += dx
            yc += dy
            last_mouse_pos = (mouse_x, mouse_y)

    sc.fill((BG_COLOR))

    edge_size_scaled = EDGE_SIZE * scale_k
    gap = edge_size_scaled * cos(radians(30)) * 2
    
    if time.time() - prev_time >= 2:
        parse()

        for worker in worker_ants:
            worker.make_move(general_map)
        prev_time = time.time()

    for hexag in hexes:
        hexag.draw()

    for hexag in home:
        x, y = hex_to_dec(hexag['q'], hexag['r'])
        draw_hex(x, y, edge_size_scaled, HEX_HOME_BG_COLOR, HEX_HOME_OUTLINE_COLOR)
    
    x, y = hex_to_dec(spot['q'], spot['r'])
    draw_hex(x, y, edge_size_scaled, HEX_SPOT_BG_COLOR, HEX_SPOT_OUTLINE_COLOR)
    
    for enemy in enemies:
        enemy.draw()

    for food in foods:
        food.draw()

    for ant in ants:
        ant.draw()

    if raiding_time:
        sc.blit(but2, (0, 0))
        if (frame_count // 10) % 2 == 0:
            print_text('ЗА РОССИЮ', (WIDTH / 2, HEIGHT / 2), 300, (255, 0, 0), 'center')
        print_text('КОНЕЦ СВО', (10, 120), 30, (255, 0, 0), 'left')
    else:
        sc.blit(but1, (0, 0))
        print_text('НАЧАТЬ СВО', (10, 120), 30, (255, 0, 0), 'left')
        
    frame_count += 1
    pygame.display.flip()
    clock.tick(FPS)