import requests
import json



def api_move(ant, move):
    url = 'https://games.datsteam.dev/api/move'
    data = {
        "moves": [
            {
                "ant": ant.id, 
                "path": [
                    {"q": el[0], 
                     "r": el[1]} for el in move
                ]
                
            }
        ]
        
    }

    headers = {"X-Auth-Token": "3c541e6b-fcbf-427e-91a0-6e261e425a60", 'Content-Type': 'application/json',}

    response = requests.post(url, json=data, headers=headers)

    print(json.dumps(data, indent=2))

    print(response.json())  # Ответ в формате JSON
