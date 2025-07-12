from algorithm import Node, Sequence, Selector, Ant
from utility import *
from math import sin, cos, pi


class EnemiesNearby(Node):
    def execute(self, ant, world):
        if world.check_enemy(ant.pos, 1): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'
    

class GoToBase(Node):
    def execute(self, ant, world):
        for i in range(len(self.home)):
            path = world.a_star(ant.pos, world.home[i])
            if path:
                ant.move(path[0])
                return 'RUNNING' if len(path) > 1 else 'SUCCESS'
        return 'FAILURE'
    

class WorkersWithRes(Node):
    def execute(self, ant, world):
        if ant.helping_ant is not None:
            return 'SUCCESS'
        else:
            return 'FAILURE'
        

class BuildRoad(Node):
    def execute(self, ant, world):
        path = world.a_star(ant.pos, (ant.pos[0] + int((ant.helping_ant.pos[0] - ant.pos[0]) / 2), ant.pos[1] + int((ant.helping_ant.pos[1] - ant.pos[1]) / 2)))
        if path:
            ant.move(path[0])
            return 'RUNNING' if len(path) > 1 else 'SUCCESS'
        return 'FAILURE'

class BuildAroundBase(Node):
    def execute(self, ant, world):
        obs_ants = list(filter(lambda x: x.type == 2, world.ants)).sort(key=lambda x: x.id)
        obs_ants = [] if obs_ants is None else obs_ants
        ind = 0
        for a in obs_ants:
            if a.id == ant.id:
                break
            ind += 1
        phi1 = pi * 0.2 * ind
        r1 = phi1 * 1.4
        q_new = int(ant.pos.x + r1 * cos(phi1))
        r_new = int(ant.pos.y + r1 * sin(phi1))
        path = world.a_star(ant.pos, Point(q_new, r_new), ant)
        if path:
            ant.move(path[0])
            return 'RUNNING' if len(path) > 1 else 'SUCCESS'
        return 'FAILURE'


class ScoutAnt(Ant):
    def __init__(self, id1, hp, pos):
        super().__init__(id1, hp, pos, 20)
        self.bt = self.create_scout_bt()
        self.radius = 4
        self.type = MY_SCOUT
        self.speed = 7
        self.helping_ant = None
        self.id = id1

    def make_move(self, world):
        self.bt.execute(self, world)

    def create_scout_bt(self):
        return Selector(children=[
            Sequence(children=[
                EnemiesNearby(),
                GoToBase()
            ]), 
            Sequence(children=[
                WorkersWithRes(), 
                BuildRoad()
            ]), 
            BuildAroundBase()
        ])