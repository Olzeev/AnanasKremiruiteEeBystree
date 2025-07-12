import requests
import json



def api_move(ant, move):
    url = 'https://games-test.datsteam.dev/api/move'
    data = {
        "moves": [
            {
                "ant": ant.id, 
                "path": [
                    {"q": el[0], "r": el[1]} for el in move
                ]
            }
        ]
        
    }

    headers = {"X-Auth-Token": "3c541e6b-fcbf-427e-91a0-6e261e425a60"}

    response = requests.post(url, json=json.dumps(data), headers=headers)

    print(response)  # Ответ в формате JSON
