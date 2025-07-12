from algorithm import Node, Sequence, Selector, Ant
from utility import *


curr_warriors = []

class IsInCombat(Node):
    def execute(self, ant, world):
        if world.check_enemy(ant.pos, 1):
            ant.in_combat = True
        else:
            ant.in_combat = False
        return 'SUCCESS' if ant.in_combat else 'FAILURE'


class HasEnoughAllies(Node):
    def __init__(self, min_allies):
        self.min_allies = min_allies

    def execute(self, ant, world):
        our_team_damage = [teammate.damage for teammate in ant.hot_point.fighters]
        our_damage = sum(our_team_damage)
        if len(our_team_damage) > 1:
            our_damage *= 1.5

        en_team_hp = [teammate.hp for teammate in ant.hot_point.enemies]
        en_hp = sum(en_team_hp)

        our_team_hp = [teammate.hp for teammate in ant.hot_point.fighters]
        our_hp = sum(our_team_hp)

        en_team_damage = [teammate.hp for teammate in ant.hot_point.enemies]
        en_damage = sum(en_team_damage)

        if our_damage >= en_hp and our_hp >= en_damage:
            return 'SUCCESS'
        return 'FAILURE'


class SOSSignalActive(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if ant.hot_point else 'FAILURE'

class ContinueFighting(Node):
    def execute(self, ant, world):
        return 'SUCCESS'

class RequestBackup(Node):
    def execute(self, ant, world):
        return 'SUCCESS'

class RetreatToBase(Node):
    """Возвращается на базу с попутным сбором ресурсов."""
    def execute(self, ant, world):
        if ant.has_food():
            path = world.find_path_to_storage(ant)
            ant.move(path[0])
            return 'RUNNING'
        return 'SUCCESS'

class RespondToSOS(Node):
    """Идёт на помощь союзникам."""
    def execute(self, ant, world):
        target = world.get_priority_sos(ant.team)
        path = world.find_path((ant.q, ant.r), target)
        ant.move(path[0])
        return 'RUNNING'


class FighterAnt(Ant):
    def __init__(self, id1, pos, hp, damage):
        super().__init__(id1, pos, hp, damage)
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
                        HasEnoughAllies(min_allies=2),
                        ContinueFighting()
                    ]),
                    RequestBackup(),  # Если сил недостаточно - запрашиваем помощь
                    RetreatToBase()  # Если помощь недоступна - отступаем
                ])
            ]),

            # Остальные приоритеты
            Sequence(children=[
                SOSSignalActive(),
                RespondToSOS()
            ]),

            Sequence(children=[
                IsEnemyVisible(),
                HasEnoughAllies(min_allies=1),
                AttackEnemy()
            ]),

            PatrolWithResourceCheck()
        ])

class HotPoint:
    def __init__(self, pos):
        self.pos = pos
        self.update()
    def update(self):
        self.border = self.get_border()
        self.enemies = self.get_enemies()
        self.fighters = self.get_fighters()

    def get_border(self):
        pass

    def get_enemies(self):
        pass

    def get_fighters(self):
        pass