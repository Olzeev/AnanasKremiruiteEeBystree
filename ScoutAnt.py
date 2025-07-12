from algorithm import Node, Sequence, Selector, Ant
from utility import *
from visualizer import *

class IsGroupTacticActive(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if world.is_raid_time else 'FAILURE'

class EnemiesNearby(Node):
    def execute(self, ant, world):
        if world.check_enemy(ant.pos, 1): #Медленный вариатн,  в теории можно пройтись по enemies и просчитать дистанцию
            return 'SUCCESS'
        return 'FAILURE'
    

class GoToBase(Node):
    def execute(self, ant, world):
        path = world.find_path_to_storage(ant)
        ant.move(path[0])
        return 'RUNNING'
    

class WorkersWithRes(Node):
    def execute(self, ant, world):
        workers = []
        for ant1 in world.ants:
            if ant1.type == 0:
                workers.append(ant1)
        workers.sort(key=lambda x: ())



class ScoutAnt(Ant):
    def __init__(self, pos, hp):
        super().__init__(pos, hp)
        self.bt = self.create_scout_bt()
        self.radius = 4
        self.type = MY_SCOUT
        self.speed = 7
        self.helping_ant_id = None

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