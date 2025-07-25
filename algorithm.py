from utility import *
import random
from api import api_move

ants_all = []

class Node:
    def execute(self, ant, world) -> str:
        """SUCCESS, FAILURE, RUNNING"""
        raise NotImplementedError


class Selector(Node):
    # Работает до SUCCESS
    def __init__(self, children):
        self.children = children

    def execute(self, ant, world):
        for child in self.children:
            result = child.execute(ant, world)
            if result == 'SUCCESS':
                return 'SUCCESS'
        return 'FAILURE'


class Sequence(Node):
    # Работает до FAILURE
    def __init__(self, children):
        self.children = children

    def execute(self, ant, world):
        for child in self.children:
            result = child.execute(ant, world)
            if result == 'FAILURE':
                return 'FAILURE'
        return 'SUCCESS'

def pizdovatNaBazu(ant, world):
    if ant.food is not None:
        for i in range(len(world.home)):
            path = world.a_star(ant.pos, Point(world.home[i][0], world.home[i][1]), ant)
            if path:
                ant.move(path)

                obs_ants = list(filter(lambda x: x.type == 2, ants_all)).sort(key=lambda x: dist(x.pos, ant.pos))
                obs_ants = [] if obs_ants is None else obs_ants
                for el in obs_ants:
                    if el.helping_ant is None:
                        el.helping_ant = ant
                        break
        return "SUCCESS"

class IsCarryingFood(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if ant.food else 'FAILURE'


class IsEnemyNear(Node):
    def execute(self, ant, world):
        pizdovatNaBazu(ant, world)
        if world.check_enemy(ant.pos, 1): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'


class IsFoodNear(Node):
    def execute(self, ant, world):
        pizdovatNaBazu(ant, world)
        if world.check_food(ant.pos, ant.radius): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'


class ReturnToBase(Node):
    def execute(self, ant, world):
        pizdovatNaBazu(ant, world)
        return 'FAILURE'


class CollectFood(Node):
    def execute(self, ant, world):
        nearest_food = world.get_nearest_food(ant.pos, ant.speed)
        if nearest_food == None:
            pos = hex_to_dec(ant.pos.x, ant.pos.y)
            data = [dist(pos, hex_to_dec(food[0], food[1])) for food in world.food]
            if len(data) != 0:
                ex_food = world.food[world.food.index(min(data))]
                nearest_food = Point(ex_food[0], ex_food[1])
        if nearest_food:
            path = ant.world.a_star(ant.pos, nearest_food)
            ant.move(path) #Отправили запрос
            pizdovatNaBazu(ant, world)
            return 'RUNNING'
        return 'FAILURE'


class Explore(Node): #Не оптимальный, переписать
    def execute(self, ant, world):
        pizdovatNaBazu(ant, world)
        while True:
            dq, dr = random.randint(-ant.speed * 5, ant.speed * 5), random.randint(-ant.speed * 5, ant.speed * 5)
            next_point = Point(ant.pos.x + dq, ant.pos.y + dr)
            if world.check_valid_point(next_point) and (dq != 0 and dr != 0):
                path = world.a_star(ant.pos, next_point, ant)
                if path is not None:
                    break
        ant.move(path) #Отправили запрос
        pizdovatNaBazu(ant, world)
        return 'RUNNING'

class Ant:
    def __init__(self, id1, hp, pos, damage):
        self.food = None
        self.pos = Point(pos[0] + TRANSITION_BIAS, pos[1] + TRANSITION_BIAS)
        self.hp = hp
        self.damage = damage
        self.id = id1

    def move(self, path):
        if self.pos.x == path[0][0] and self.pos.y == path[0][1]:
            return
        api_move(self, [(el[0] - TRANSITION_BIAS * 2, el[1] - TRANSITION_BIAS * 2) for el in path])

    def update(self, hp, pos, food):
        self.hp = hp
        self.pos = Point(pos[0] + TRANSITION_BIAS, pos[1] + TRANSITION_BIAS)
        self.food = food


class WorkerAnt(Ant):
    def __init__(self, id1, pos, hp, damage):
        super().__init__(id1, pos, hp, damage)
        self.bt = self.create_worker_bt()
        self.radius = 1
        self.type = MY_WORKER
        self.speed = 5
        self.id = id1

    def make_move(self, world):
        self.bt.execute(self, world)

    def create_worker_bt(self):
        return Selector(children=[
            Sequence(children=[
                IsEnemyNear(),
                ReturnToBase()
            ]),

            Sequence(children=[
                IsCarryingFood(),
                ReturnToBase()
            ]),

            Sequence(children=[
                IsFoodNear(),
                CollectFood()
            ]),

            Explore()
        ])