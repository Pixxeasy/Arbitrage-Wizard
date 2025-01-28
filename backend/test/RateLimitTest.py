import time
from time import sleep

import ccxt.async_support as ccxt
import asyncio
from ccxt import RateLimitExceeded
from datetime import datetime

times = []

def test_async():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_mexc_rate_limit())

async def limited_request(exchange, semaphore, interval):
    async with semaphore:
        resp = await do_request(exchange)

    return resp

async def test_mexc_rate_limit():
    exchange = ccxt.mexc({"enableRateLimit": True})

    max_requests_per_10_seconds = 100
    request_interval = 10 / max_requests_per_10_seconds  # Interval in seconds (e.g., 0.02s for 50 req/sec)
    semaphore = asyncio.Semaphore(3)

    tasks = []


    tasks = [limited_request(exchange, semaphore, request_interval) for _ in range(500)]  # 120 requests
    responses = await asyncio.gather(*tasks)

    avg = sum(times) / len(times)
    print(f"{avg} ms")

async def do_request(exchange):
    time_start = datetime.now().timestamp()
    ob = await exchange.fetch_order_book("BTC/USDT")
    times.append((datetime.now().timestamp()) - time_start)
    return ob