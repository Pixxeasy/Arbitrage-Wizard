import asyncio
import json
import logging
import sys

from app.database.db_connector import connect
from scanner import util
from scanner.scan_runner import ScanRunner

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def launch():
    logger = logging.getLogger("Launcher")
    logging.basicConfig(level=logging.INFO)
    logger.info('Starting Scanner Module')

    logger.info('Load Config')
    with open('conf/config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)

    util.DEBUG = config['debug']

    logger.info('Connect to database')
    session = connect(db_type=config['db_type'], db_name=config['db_name'])
    runner = ScanRunner(config["search_interval"], session())
    await runner.start(config["exchanges"])
    session().close()
    await  runner.stop()


asyncio.run(launch())
