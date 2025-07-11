
import cv2
import numpy as np
from player import requester, game_state, ship_controllers


class MapVisualizer:

    def __init__(self):
        map_size = requester.current_state['mapSize']
        self.map_width = int(map_size['x'])
        self.map_height = int(map_size['y'])
        self.map_name = requester.current_state['name']
        cv2.namedWindow("sakivonuchie")
        cv2.resizeWindow("sakivonuchie", 1000, 1000)
        cv2.namedWindow("bebebe")
        cv2.resizeWindow("bebebe", 1000, 1000)
        self.image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        self.info_image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        self.x_k = 1000/self.map_width
        self.y_k = 1000/self.map_height

    def convert_pos(self, x, y):
        return (int(x*self.x_k), int(y*self.y_k))

    def draw_velocity(self, img, x, y, vx, vy, color=(0, 0, 0)):

        end_point = self.convert_pos(int(x + vx * 10), int(y + vy * 10))
        cv2.arrowedLine(img, self.convert_pos(int(x), int(y)),
                        end_point, color, 1, tipLength=0.3)

    def draw_info(self):

        self.info_image[:, :, 0] = 255
        self.info_image[:, :, 1] = 255
        self.info_image[:, :, 2] = 255
        cnt = 1
        for ship in ship_controllers:
            cv2.putText(self.info_image, f"SHIP ID: {ship.ship_id}; alive: {ship.alive}; hp: {ship.health}; velocity: { str(ship.velocity)};", (20, cnt*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(self.info_image, f"gold_near: {str(ship.getNearestGold())}", (20, (cnt+1)*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(self.info_image, f"shield_cd: {str(ship.shieldCooldown)}; attack_cd: {str(ship.attackCooldown)};", (20, (cnt+2)*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(self.info_image, f"target: {str(ship.target["enemy"] if "enemy"  in ship.target else None)}", (20, (cnt+3)*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            cnt += 4

        cv2.putText(self.info_image, f"POINTS: {game_state.total_points}", (20, 800), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 1)

    def draw(self):
        data = requester.current_state
        if not data:
            return

        self.image[:, :, 0] = 255
        self.image[:, :, 1] = 255
        self.image[:, :, 2] = 255

        for anomaly in data['anomalies']:
            center = self.convert_pos(int(anomaly['x']), int(anomaly['y']))
            cv2.circle(self.image, center, int(
                anomaly['radius'])//9, (255, 0, 0), -1)  # синий цвет
            # cv2.circle(self.image, center, int(
            #     anomaly['effectiveRadius'])//9, (100, 255, 255), 2)  # синий цвет
            self.draw_velocity(
                self.image, anomaly['x'], anomaly['y'], anomaly['velocity']['x'], anomaly['velocity']['y'], color=(255, 0, 0))

           # cv2.putText(self.image, f"ID: {
            # anomaly['id']}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        for ship in ship_controllers:
            color = (0, 255, 0)
            if not ship.alive:
                color = (0, 0, 0)
            elif ship.attackCooldown > 0:
                color = (255, 0, 255)
            center = self.convert_pos(ship.position.x, ship.position.y)
            cv2.circle(self.image, center, 3, color, -1)  # зеленый круг
            cv2.circle(self.image, center, int(game_state.attackRange*self.x_k), color, 1)  # зеленый круг
            self.draw_velocity(self.image, ship.position.x, ship.position.y, ship.velocity.x, ship.velocity.y, color=color)
            cv2.putText(self.image, f"ID: { ship.ship_id}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        targeted = [x.target["enemy"]
                    if "enemy" in x.target else None for x in ship_controllers]
        for enemy in game_state.enemies:
            center = self.convert_pos(
                int(enemy.position.x), int(enemy.position.y))
            # красный круг для врагов

            cv2.circle(self.image, center, 3, (0, 0, 255), -1)
            self.draw_velocity(
                self.image, enemy.position.x, enemy.position.y, enemy.velocity.x, enemy.velocity.y, color=(0, 0, 255))
            cv2.putText(self.image, f"HP: { enemy.health}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        for enemy in targeted:
            if enemy is None:
                continue
            print(f"Targeted enemy: {enemy}")
            center = self.convert_pos(
                int(enemy.position.x), int(enemy.position.y))
            # красный круг для врагов

            cv2.circle(self.image, center, 10, (203, 2, 246), -1)

        for bounty in game_state.bounties:
            center = self.convert_pos(
                int(bounty.position.x), int(bounty.position.y))
            cv2.circle(self.image, center, 2, (0, 255, 255), -1)
            # cv2.putText(self.image, str(bounty.points), center, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        self.draw_info()
        cv2.imshow("bebebe", self.info_image)
        cv2.imshow("sakivonuchie", self.image)
        if cv2.waitKey(320) & 0xFF == ord('q'):
            return
