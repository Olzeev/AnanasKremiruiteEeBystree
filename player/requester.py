import time
import queue
import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class UltraRequester:
    TOKEN: str = "3c541e6b-fcbf-427e-91a0-6e261e425a60"
    BASE_URL: str = "https://games-test.datsteam.dev/api"

    async def post(self, url: str, body: Optional[dict] = {}):
        async with self.session.post(
            json=body, headers={"X-Auth-Token": self.TOKEN}
        ) as r:
            data = await r.text()
            logger.debug(f"[POST] response: {data}, status: {r.status}")
            if r.status != 200:
                return {"cooldown": True}
            data["cooldown"] = False
            return data

    async def get(self, url: str, body: Optional[dict] = {}):
        async with self.session.get(
            json=body, headers={"X-Auth-Token": self.TOKEN}
        ) as r:
            data = await r.text()
            logger.debug(f"[POST] response: {data}, status: {r.status}")
            if r.status != 200:
                return {"cooldown": True}
            data["cooldown"] = False
            return data

    async def register(self):
        try:
            return await self.post("/register")
        except BaseException as e:
            logger.error(f"Can't get arena, details: {str(e)}")

    async def arena(self):
        try:
            return await self.get("/arena")
        except BaseException as e:
            logger.error(f"Can't get arena, details: {str(e)}")

    async def move(self, data):
        try:
            return await self.post("/move", data)
        except BaseException as e:
            logger.error(f"Can't move, details: {str(e)}")

    async def logs(self):
        try:
            return await self.get("/logs")
        except BaseException as e:
            logger.error(f"Can't get logs, details: {str(e)}")

    def __init__(self):
        self.body: dict = {}
        self.session = aiohttp.ClientSession(self.BASE_URL)
        self.dt = time.time()
        self.requests_queue = queue.Queue()
        self.start()
        self.current_state = {}
        self.dt_metrics = 0
        self.update_flag = True

    def request(self, body: dict):
        self.requests_queue.put_nowait(body)
    

    async def move(self):
        r = await self.post()
        if not r["cooldown"]:
            # update gamestate here
            self.body = {}
