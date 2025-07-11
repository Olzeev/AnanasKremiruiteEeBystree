from player.types import Point, Enemy, Food, FoodPoint
from typing import List


class GameState:
    enemies: List[Enemy]
    food_points: List[FoodPoint]

    def update_from_state(self, state: dict):
        self.enemies = [
            Enemy(
                attack=e["attack"],
                food=Food(food_type=e["food"]["type"], amount=e["food"]["type"]),
                health=e["health"],
                coord=Point(e["q"], e["r"]),
                type=e["type"],
            )
            for e in state["enemies"]
        ]
        self.food_points = [FoodPoint(Food())]
        self.anomalies = [Anomalie(e_radius=a["effectiveRadius"],
                                   id=a["id"],
                                   radius=a["radius"],
                                   strength=a["strength"],
                                   velocity=Vector(
                                       a["velocity"]["x"], a["velocity"]["y"]),
                                   position=Point(a["x"], a["y"])) for a in state["anomalies"]]
        self.attackCooldown = state["attackCooldownMs"]
        self.attackDamage = state["attackDamage"]
        self.attackExplosionRadius = state["attackExplosionRadius"]
        self.attackRange = state["attackRange"]
        self.bounties = [GoldPoint(points=p["points"],
                                   radius=p["radius"],
                                   position=Point(p["x"], p["y"])) for p in state["bounties"]]
        self.enemies = [EnemyShip(health=e["health"],
                                  killBounty=e["killBounty"],
                                  shieldLeft=e["shieldLeftMs"],
                                  alive=e["status"] == "alive",
                                  velocity=Vector(
                                      e["velocity"]["x"], e["velocity"]["y"]),
                                  position=Point(e["x"], e["y"])) for e in state["enemies"]]
        self.mapSize = Point(state["mapSize"]["x"], state["mapSize"]["y"])
        self.maxAccel = state["maxAccel"]
        self.maxSpeed = state["maxSpeed"]
        self.total_points = state["points"]
        self.reviveTimeout = state["reviveTimeoutSec"]
        self.shieldCooldown = state["shieldCooldownMs"]
        self.shieldTime = state["shieldTimeMs"]
        self.transportRadius = state["transportRadius"]
        self.wantedList = [EnemyShip(health=e["health"],
                                  killBounty=e["killBounty"],
                                  shieldLeft=e["shieldLeftMs"],
                                  alive=e["status"] == "alive",
                                  velocity=Vector(
                                      e["velocity"]["x"], e["velocity"]["y"]),
                                  position=Point(e["x"], e["y"])) for e in state["wantedList"]]
        for e in self.enemies:
            if not e.alive:
                self.enemies.remove(e)
