from utility import *

class Node:
    def execute(self, ant, game_state) -> str:
        """SUCCESS, FAILURE, RUNNING"""
        raise NotImplementedError


class Selector(Node):
    # Работает до SUCCESS
    def __init__(self, children):
        self.children = children

    def execute(self, ant, game_state):
        for child in self.children:
            result = child.execute(ant, game_state)
            if result == 'SUCCESS':
                return 'SUCCESS'
        return 'FAILURE'


class Sequence(Node):
    # Работает до FAILURE
    def __init__(self, children):
        self.children = children

    def execute(self, ant, game_state):
        for child in self.children:
            result = child.execute(ant, game_state)
            if result == 'FAILURE':
                return 'FAILURE'
        return 'SUCCESS'

class IsCarryingFood(Node):
    def execute(self, ant, _):
        return 'SUCCESS' if ant.food else 'FAILURE'


class IsEnemyNear(Node):
    def execute(self, ant, game_state):
        if ant.world.check_enemy(ant.pos, 1): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'


class IsFoodNear(Node):
    def execute(self, ant, game_state):
        if ant.world.check_food(ant.pos, ant.radius): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'


class ReturnToBase(Node):
    def execute(self, ant, game_state):
        path = ant.world.a_star(ant.pos, game_state.home)
        if path:
            ant.move(path[0])
            return 'RUNNING' if len(path) > 1 else 'SUCCESS'
        return 'FAILURE'


class CollectFood(Node):
    def execute(self, ant, game_state):
        nearest_food = find_nearest_food(ant, game_state.food)
        if nearest_food:
            path = ant.world.a_star(ant.pos, nearest_food)
            ant.move(path[0])
            return 'RUNNING'
        return 'FAILURE'


class Explore(Node):
    def execute(self, ant, _):
        ant.move((random_q, random_r))
        return 'RUNNING'

class Ant:
    def __init__(self, pos, world):
        self.food = None
        self.pos = pos
        self.world = Map(world)

class WorkerAnt(Ant):
    def __init__(self, pos, world):
        super().__init__(pos, world)
        self.bt = self.create_worker_bt()
        self.radius = 1
        self.type = MY_WORKER

    def make_move(self, game_state):
        self.bt.execute(self, game_state)

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