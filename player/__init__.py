import logging
import sys

# from player.requester import UltraRequester
# from player.gamestate import GameState


logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Вывод в консоль
            logging.FileHandler('app.log')      # Запись в файл
        ]
    )

# requester = UltraRequester(0.32)
# while requester.current_state == {}:
#     print("Waiting for not null state")
# ship_controllers = [ShipController(x["id"])
#                     for x in requester.current_state["transports"]]
# game_state = GameState()
