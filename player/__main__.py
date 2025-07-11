from player.requester import UltraRequester
from player.controller import GameController


import time
import asyncio
import logging


requester: UltraRequester

logger = logging.getLogger(__name__)


async def worker():
    start_t = time.time()
    while True:
        if time.time() - start_t >= 2:
            start_t = time.time()
            await GameController.tick()


async def main():
    requester = UltraRequester()
    logger.info("started server")
    await asyncio.create_task(worker())


if __name__ == "__main__":
    asyncio.run(main())
