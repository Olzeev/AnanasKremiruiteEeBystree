from algorithm import Node, Sequence, Selector, IsEnemyNear, IsFoodNear, CollectFood, Ant
from utility import *

class IsGroupTacticActive(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if world.is_raid_time else 'FAILURE'

class RaidEnemyAnthill(Node):
    def execute(self, ant, world):
        target = world.find_nearest_enemy_anthill(ant.q, ant.r) #Доделать
        if target:
            path = world.a_star(ant.pos, target, ant)
            if path:
                ant.move(path)
                return 'RUNNING'
        return 'FAILURE'

class IsForceSufficient(Node):
    def execute(self, ant, world):
        nearby_allies = world.count_nearby_ants(ant.q, ant.r, ant_type='Warrior', radius=3)
        return 'SUCCESS' if nearby_allies >= 3 else 'FAILURE'  # Минимум 3 бойца


class RetreatToGroup(Node):
    def execute(self, ant, world):
        ally = world.find_nearest_ally(ant.q, ant.r, ant_type='Warrior')
        if ally:
            path = world.find_path((ant.q, ant.r), (ally.q, ally.r))
            ant.move(path[0])
            return 'RUNNING'
        return 'FAILURE'


class WarriorAnt(Ant):
    def __init__(self, pos, hp):
        super().__init__(pos, hp)
        self.bt = self.create_warrior_bt()
        self.radius = 1
        self.type = MY_FIGHTER
        self.speed = 4

    def make_move(self, world):
        self.bt.execute(self, world)

    def create_warrior_bt():
        return Selector(children=[
            Sequence(children=[
                IsGroupTacticActive(),
                RaidEnemyAnthill()
            ]),

            Selector(children=[
                Sequence(children=[
                    IsEnemyNear(),
                    IsForceSufficient(),
                    AttackEnemy()
                ]),
                Sequence(children=[
                    IsEnemyNear(),
                    RetreatToGroup()
                ]),

                Sequence(children=[
                    IsFoodNear(),
                    CollectFood()
                ]),

                # Дефолтное поведение
                PatrolZone()  # Периодически возвращаться на базу, если есть еда
            ])
        ])