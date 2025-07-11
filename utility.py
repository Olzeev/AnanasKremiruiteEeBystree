import heapq

HEIGHT = 5000
WIDTH = 5000


DIRT = 1
ACID = 2
STONE = 3
ANTHILL = 4
EN_ANTHILL = 0
HEX_TYPES = [ANTHILL, None, DIRT, ACID, STONE]
MY_SCOUT = 5
MY_FIGHTER = 6
MY_WORKER = 7
MY_UNITS = [MY_WORKER, MY_FIGHTER, MY_SCOUT]
EN_SCOUT = 8
EN_FIGHTER = 9
EN_WORKER = 10
EN_UNITS = [EN_WORKER, EN_FIGHTER, EN_SCOUT]
APPLE = 11
BREAD = 12
NECTAR = 13
FOODS = [APPLE, BREAD, NECTAR]
WORKER = [MY_WORKER, EN_WORKER]
SCOUT = [MY_SCOUT, EN_SCOUT]
FIGHTER = [MY_FIGHTER, EN_FIGHTER]

TRANSITION_BIAS = 1000

def dist(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2
def get_damage(type):
    if type == EN_WORKER:
        return 30
    if type == EN_SCOUT:
        return 20
    if type == EN_FIGHTER:
        return 70
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Map:
    def __init__(self, world, home, food):
        self.world = world
        self.home = home
        self.food = food

    def update(self, ants, enemies, foods, hexes, home):
        for i in range(HEIGHT):
            for j in range(WIDTH):
                for UN in MY_UNITS:
                    if UN in self.world[i][j]:
                        self.world[i][j].remove(UN)
                for UN in EN_UNITS:
                    if UN in self.world[i][j]:
                        self.world[i][j].remove(UN)
                
        for ant in ants:
            self.world[ant.r + TRANSITION_BIAS][ant.q + TRANSITION_BIAS].append(MY_UNITS[ant.type])
        for enemy in enemies:
            self.world[enemy.r + TRANSITION_BIAS][enemy.q + TRANSITION_BIAS].append(EN_UNITS[enemy.type])
        for food in foods:
            self.world[food.r + TRANSITION_BIAS][food.q + TRANSITION_BIAS].append(FOODS[food.type - 1])
        for hexag in hexes:
            if hexag.type == 2: # пустой
                for f in FOODS:
                    if f in self.world[hexag.r + TRANSITION_BIAS][hexag.q + TRANSITION_BIAS]:
                        self.world[hexag.r + TRANSITION_BIAS][hexag.q + TRANSITION_BIAS].remove(f)
            if hexag.type == 1: # муравейник
                if (hexag.q, hexag.r) in list(map(lambda x: (x['q'], x['r']), home)):
                    self.world[hexag.r + TRANSITION_BIAS][hexag.q + TRANSITION_BIAS].append(ANTHILL)
                else:
                    self.world[hexag.r + TRANSITION_BIAS][hexag.q + TRANSITION_BIAS].append(EN_ANTHILL)
            else:
                self.world[hexag.r + TRANSITION_BIAS][hexag.q + TRANSITION_BIAS].append(HEX_TYPES[hexag.type - 1])
        
        



    def get_available_points(self, el):
        if el.y % 2 == 1:
            directions = [
                Point(el.x + 1, el.y),
                Point(el.x + 1, el.y + 1),
                Point(el.x + 1, el.y - 1),
                Point(el.x - 1, el.y),
                Point(el.x, el.y + 1),
                Point(el.x, el.y - 1),
            ]
        else:
            directions = [
                Point(el.x, el.y + 1),
                Point(el.x, el.y - 1),
                Point(el.x + 1, el.y),
                Point(el.x - 1, el.y),
                Point(el.x - 1, el.y - 1),
                Point(el.x - 1, el.y + 1),
            ]
        directions = [el for el in directions if self.check_valid_point(el)]
        return  directions
    def cost(self, data, ant, pos):
        if len(data) == 0:
            return 0
        if STONE in data or EN_SCOUT in data or EN_FIGHTER in data or EN_WORKER in data or ant.type in data:
            return float("inf")
        if ACID in data and ant.hp <= 20:
            return float("inf")
        if self.check_anthill(pos, 2) and ant.hp <= 20:
            return float("inf")
        if sum([get_damage(el) for el in self.get_enemies_in_rad(pos, 1)]) * 1.5 >= ant.hp:
            return float("inf")
        reward = 0
        for el in data:
            if DIRT == el:
                reward += 2
            if ANTHILL == el:
                reward += 1
            if ACID == el:
                reward += 11
            if (ant.food == None or ant.food == APPLE) and APPLE == el:
                reward -= 20
            if (ant.food == None or ant.food == BREAD) and BREAD == el:
                reward -= 30
            if (ant.food == None or ant.food == NECTAR) and NECTAR == el:
                reward -= 70
        return reward

    def heuristic(self, a, b):
        return (abs(a[0] - b[0]) + abs(a[1] - b[1])) // 2

    def a_star(self, start, goal, ant):
        if not self.check_valid_point(start):
            return None
        if not self.check_valid_point(goal):
            return None
        start = (start.x, start.y)
        goal = (goal.x, goal.y)

        if self.cost(self.world[goal[0]][goal[1]], ant, Point(goal[0], goal[1])) == float('inf'):
            return None

        open_set = []
        heapq.heappush(open_set, (0, start[0], start[1]))

        # Для отслеживания пути
        came_from = {}

        # Стоимость пути от start до текущей точки
        g_score = {(start[0], start[1]): 0}

        # Оценочная стоимость start -> goal через текущую
        f_score = {(start[0], start[1]): self.heuristic(start, goal)}

        while open_set:
            _, current_q, current_r = heapq.heappop(open_set)
            current = (current_q, current_r)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for re in self.get_available_points(Point(current_q, current_r)):
                neighbor_q, neighbor_r = re.x, re.y

                if not (0 <= neighbor_q <= WIDTH and 0 <= neighbor_r <= HEIGHT):
                    continue

                neighbor_type = self.world[neighbor_q][neighbor_r]
                if self.cost(neighbor_type, ant, Point(neighbor_q, neighbor_r)) == float('inf'):
                    continue

                tentative_g_score = g_score[current] + self.cost(neighbor_type, ant, Point(neighbor_q, neighbor_r))

                if (neighbor_q, neighbor_r) not in g_score or tentative_g_score < g_score[(neighbor_q, neighbor_r)]:
                    came_from[(neighbor_q, neighbor_r)] = current
                    g_score[(neighbor_q, neighbor_r)] = tentative_g_score
                    f_score[(neighbor_q, neighbor_r)] = tentative_g_score + self.heuristic((neighbor_q, neighbor_r), goal)
                    heapq.heappush(open_set, (f_score[(neighbor_q, neighbor_r)], neighbor_q, neighbor_r))

        return None
    def check_enemy(self, pos, rad):
        for unit in EN_UNITS:
            return self.check_item(pos, rad, unit)

    def check_anthill(self, pos, rad):
        return  self.check_item(pos, rad, ANTHILL)

    def check_food(self, pos, rad):
        for food in FOODS:
            if self.check_item(pos, rad, food):
                return True
        return False

    def check_item(self, pos, rad, item):
        next_points = []
        qur_points = [pos]
        used_points = [pos]

        for i in range(rad):
            for el in qur_points:
                directions = self.get_avaliable_points(el)
                if item in self.world[el.y][el.x]:
                    return True
                for new_pos in directions:
                    if self.check_valid_point(new_pos) and new_pos not in used_points:
                        used_points.append(new_pos)
                        next_points.append(new_pos)

            qur_points = next_points
            next_points = []
            '''
                    enemy_positions = []
                    for point in used_points:
                        if point != pos and self.is_enemy(point):
                            enemy_positions.append(point)

                    return enemy_positions
                    '''
        return False

    def get_nearest_food(self, pos, rad):
        next_points = []
        qur_points = [pos]
        used_points = [pos]

        for i in range(rad):
            for el in qur_points:
                directions = self.get_avaliable_points(el)
                if APPLE in self.world[el.y][el.x] or BREAD in self.world[el.y][el.x] or NECTAR in self.world[el.y][el.x]:
                    return el
                for new_pos in directions:
                    if self.check_valid_point(new_pos) and new_pos not in used_points:
                        used_points.append(new_pos)
                        next_points.append(new_pos)

            qur_points = next_points
            next_points = []
        return None
    def get_enemies_in_rad(self, pos, rad):
        next_points = []
        qur_points = [pos]
        used_points = [pos]

        for i in range(rad):
            for el in qur_points:
                directions = self.get_avaliable_points(el)
                for new_pos in directions:
                    if self.check_valid_point(new_pos) and new_pos not in used_points:
                        used_points.append(new_pos)
                        next_points.append(new_pos)

            qur_points = next_points
            next_points = []

        enemy_positions = []
        for point in used_points:
            if point != pos and self.world[point.y][point.x] in EN_UNITS:
                enemy_positions.append(point)

        return enemy_positions
    def check_valid_point(self, pos):
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            return True
        return False