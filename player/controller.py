import logging

from player.requester import UltraRequester
from player.ant import Ant
from player.types import Point, Food
from player.gamestate import GameState

from typing import Optional, List

logger = logging.getLogger(__name__)


class GameController:
    ants = []
    next_body: dict

    def __init__(self, requester: UltraRequester):
        self.requester = requester
        self.next_body = {}

    async def getLogs(self):
        # (.) (.) <--- сиськи
        r = await self.requester.logs()
        logger.debug(f"Logs: {r}")

    async def getArena(self):
        r = await self.requester.logs()
        logger.debug(f"Arena: {r}")

    async def updateState(self, ants: Optional[List]):
        if ants is None:
            state = await self.getArena()
            ants = state["ants"]
        self.ants.clear()
        for a in ants:
            new_ant = Ant(ant_id=a["id"], ant_type=a["type"])
            new_ant.coord = Point(a["q"], a["r"])
            new_ant.food = Food(food_type=a["food"]["type"], amount=a["food"]["amount"])
            new_ant.health = a["health"]
            new_ant.lastAttack = Point(a["lastAttack"]["q"], a["lastAttack"]["r"])
            new_ant.lastMove = [Point(p["q"], p["r"]) for p in a["lastMove"]]
            self.ants.append(new_ant)

    async def tick(self, world: GameState):
        r = {"moves": []}
        for a in self.ants:
            r["moves"].append(a.command)
            a.command = {}
        resp = await self.requester.move(data=self.next_body)
        self.updateState(resp["ants"])
