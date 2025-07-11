from player.types import Point, Food
from typing import List, Dict


class Ant:
    coord: Point
    command: Dict
    health: int
    attack: int
    carry: int
    view_range: int
    speed: int
    food: Food
    lastMove: List[Point]
    lastAttack: List[Point]
    type: int

    def __init__(self, ant_id: int, ant_type: int):
        self.id = ant_id
        self.type = ant_type
        self.command = {}
        match ant_type:
            case 0:
                self.attack = 30
                self.carry = 8
                self.view_range = 1
                self.speed = 5
            case 1:
                self.attack = 70
                self.carry = 2
                self.view_range = 1
                self.speed = 4
            case 2:
                self.attack = 20
                self.carry = 2
                self.view_range = 4
                self.speed = 7

    def move(self, path: List[Point]):
        self.command = {"ant": self.id, "path": [{"q": h.x, "r": h.y} for h in path]}
