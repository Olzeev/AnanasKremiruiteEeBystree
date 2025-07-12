from algorithm import Node, Sequence, Selector, IsEnemyNear, IsFoodNear, CollectFood, Ant, ReturnToBase
from utility import *


curr_warriors = []

class IsInCombat(Node):
    def execute(self, ant, world):
        if world.check_enemy(ant.pos, 1):
            ant.in_combat = True
        else:
            ant.in_combat = False
        return 'SUCCESS' if ant.in_combat else 'FAILURE'


class SOSSignalActive(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if ant.hot_point else 'FAILURE'

class ContinueFighting(Node):
    def execute(self, ant, world):
        ant.hot_point.update(world)
        return 'SUCCESS'

class RequestBackup(Node):
    def execute(self, ant, world):
        nearest_teammates = world.get_teammates_in_rad(ant.pos, ant.radius + 2)
        nearest_teammates = [teammate for teammate in curr_warriors if teammate.pos in nearest_teammates]
        req_teammates = []
        enemy = world.get_enemies_in_rad[0]
        if ant.hot_point:
            new_hotpoint = ant.hot_point
        else:
            new_hotpoint = HotPoint(enemy)
            new_hotpoint.enemies.appand(enemy)
            new_hotpoint.fighters.append(ant)
        for teammate in nearest_teammates:
            if not teammate.in_combat and teammate not in new_hotpoint.fighters:
                req_teammates.append(teammate)
                teammate.hot_point = new_hotpoint
                new_hotpoint.fighters.append(teammate)
        ant.hot_point = new_hotpoint
        our_team_damage = [teammate.damage for teammate in ant.hot_point.fighters]
        our_damage = sum(our_team_damage)
        if len(our_team_damage) > 1:
            our_damage *= 1.5

        en_hp = len(ant.hot_point.fighters) * 120

        our_team_hp = [teammate.hp for teammate in ant.hot_point.fighters]
        our_hp = sum(our_team_hp)

        en_damage = len(ant.hot_point.enemies) * 40

        if our_damage >= en_hp and our_hp >= en_damage:
            return 'SUCCESS'
        ant.hot_point = None
        for teammate in req_teammates:
            teammate.hot_point = None
        return 'FAILURE'


class RespondToSOS(Node):
    def execute(self, ant, world):
        if ant.hot_point:
            for border in ant.hot_point.border:
                path = world.a_star(ant.pos, border, ant)
                if path:
                    ant.move(path)
                    return 'SUCCESS'
        ant.hot_point.fighters.remove(ant)
        ant.hot_point = None
        return 'FAILURE'

class IsEnemyVisible(Node):
    def execute(self, ant, world):
        if world.check_enemy(ant.pos, 4): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'


class PatrolWithResourceCheck(Node):
    def __init__(self, patrol_radius=5):
        self.patrol_radius = patrol_radius
        self.patrol_points = []
        self.current_point_index = 0
        self.return_home_counter = 0
        self.max_patrol_cycles_before_return = 3

    def execute(self, ant, world):
        if ant.food:
            return ReturnToBase().execute(ant, world)

        if self.return_home_counter >= self.max_patrol_cycles_before_return:
            self.return_home_counter = 0
            return ReturnToBase().execute(ant, world)

        if not self.patrol_points:
            self._generate_patrol_points(ant, world)

        if 'SUCCESS' == IsFoodNear().execute(ant, world):
            return 'SUCCESS'

        current_target = self.patrol_points[self.current_point_index]
        path = world.a_star(ant.pos, Point(current_target[0], current_target[1]), ant)

        if path and len(path) > 0:
            ant.move(path)
            if ant.pos == current_target:
                self.current_point_index = (self.current_point_index + 1) % len(self.patrol_points)
                self.return_home_counter += 1
            return 'SUCCESS'

        self._generate_patrol_points(ant, world)
        return 'FAILURE'

    def _generate_patrol_points(self, ant, world):
        self.patrol_points = []
        base_pos = world.home[0]

        offsets = [
            (self.patrol_radius, 0),
            (0, self.patrol_radius),
            (-self.patrol_radius, 0),
            (0, -self.patrol_radius)
        ]

        for dq, dr in offsets:
            q = base_pos[0] + dq
            r = base_pos[1] + dr
            if world.is_valid_position(Point(q, r)):
                self.patrol_points.append((q, r))

        if not self.patrol_points:
            self.patrol_points.append(base_pos)

        self.current_point_index = 0


class WarriorAnt(Ant):
    def __init__(self, id1, pos, hp, damage):
        super().__init__(pos, hp, damage)
        self.bt = self.create_warrior_bt()
        self.radius = 1
        self.id = id1
        self.type = MY_FIGHTER
        self.speed = 4
        self.in_combat = False
        self.hot_point = None

    def make_move(self, world):
        self.bt.execute(self, world)

    def create_warrior_bt(self):
        return Selector(children=[
            # Главный боевой Sequence (проверяет IsInCombat только один раз)
            Sequence(children=[
                IsInCombat(),  # Проверяем один раз в начале
                Selector(children=[  # Варианты действий в бою
                    Sequence(children=[
                        RequestBackup(min_allies=2),
                        ContinueFighting()
                    ]),
                    ReturnToBase()  # Если помощь недоступна - отступаем
                ])
            ]),

            # Остальные приоритеты
            Sequence(children=[
                SOSSignalActive(),
                RespondToSOS()
            ]),

            Sequence(children=[
                IsEnemyVisible(),
                RequestBackup(min_allies=1),
                RespondToSOS()
            ]),

            PatrolWithResourceCheck()
        ])

class HotPoint:
    def __init__(self, pos):
        self.pos = pos
        self.enemies = [pos]
        self.border = []
        self.fighters = []
        self.update()
    def update(self, world):
        self.upd_border(world)

    def upd_border(self, world):
        self.border = []
        next_enemy = self.enemies
        next_next_enemy = []
        self.enemies = []
        while len(next_enemy)!=0:
            for enemy in next_enemy:
                if world.world[enemy.y][enemy.x] in EN_UNITS:
                    self.enemies.append(enemy)
                for pos in world.get_available_points(enemy):
                    if pos not in self.border and pos not in self.enemies:
                        self.border.append(pos)
                    if world.world[pos.y][pos.x] in EN_UNITS:
                        self.enemies.append(pos)
                        next_next_enemy.append(pos)
            next_enemy = next_next_enemy
            next_next_enemy =[]


