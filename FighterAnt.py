from algorithm import Node, Sequence, Selector, IsEnemyNear, IsFoodNear, CollectFood, Ant
from utility import *
from visualizer import *


class IsInCombat(Node):
    def execute(self, ant, world):
        return 'SUCCESS' if ant.in_combat else 'FAILURE'


class HasEnoughAllies(Node):
    def __init__(self, min_allies):
        self.min_allies = min_allies

    def execute(self, ant, world):
        our_team_damage = [teammate.damage for teammate in ant.hot_point.fighters]
        our_damage = sum(our_team_damage)
        if len(our_team_damage) > 1:
            our_damage *= 1.5

        en_team_hp = [teammate.damage for teammate in ant.hot_point.enemies]
        en_damage = sum(en_team_damage)
        if len(en_team_damage) > 1:
            en_damage *= 1.5

        allies = world.count_nearby_allies(ant.q, ant.r, radius=2)
        return 'SUCCESS' if allies >= self.min_allies else 'FAILURE'


class SOSSignalActive(Node):
    """Проверяет активные сигналы о помощи."""

    def execute(self, ant, world):
        return 'SUCCESS' if world.get_sos_signals(ant.team) else 'FAILURE'

class ContinueFighting(Node):
    """Продолжает текущий бой."""
    def execute(self, ant, world):
        ant.attack(world.get_nearest_enemy(ant.q, ant.r))
        return 'SUCCESS'

class RequestBackup(Node):
    """Отправляет запрос подкрепления."""
    def execute(self, ant, world):
        world.send_sos(ant.q, ant.r, ant.team)
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


class WarriorAnt(Ant):
    def __init__(self, pos, hp, damage):
        super().__init__(pos, hp, damage)
        self.bt = self.create_warrior_bt()
        self.radius = 1
        self.type = MY_FIGHTER
        self.speed = 4
        self.in_combat = False
        self.hot_point = None

    def make_move(self, world):
        self.bt.execute(self, world)

    def create_warrior_bt(self):
        return Selector(children=[
            # Приоритет 1: Текущий бой
            Sequence(children=[
                IsInCombat(),
                HasEnoughAllies(min_allies=2),
                ContinueFighting()
            ]),

            # Приоритет 2: Запрос помощи
            Sequence(children=[
                IsInCombat(),
                RequestBackup()
            ]),

            # Приоритет 3: Отступление
            Sequence(children=[
                IsInCombat(),
                RetreatToBase()
            ]),

            # Приоритет 4: Ответ на SOS
            Sequence(children=[
                SOSSignalActive(),
                RespondToSOS()
            ]),

            # Приоритет 5: Новые угрозы
            Sequence(children=[
                IsEnemyVisible(),
                HasEnoughAllies(min_allies=1),
                AttackEnemy()
            ]),

            # Приоритет 6: Патрулирование
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