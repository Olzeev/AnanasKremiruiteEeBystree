import requests

r = requests.post(
        url="https://games.datsteam.dev/api/register",
        json={},
        headers={"X-Auth-Token": "3c541e6b-fcbf-427e-91a0-6e261e425a60"},
    )
print(r.json())