import asyncio
import aiohttp

from utils import cache


@cache.async_cache()
async def query(url, method="get", res_method="text", *args, **kwargs):
    async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
        async with getattr(session, method.lower())(url, *args, **kwargs) as res:
            return await getattr(res, res_method)()


async def get(url, *args, **kwargs):
    return await query(url, "get", *args, **kwargs)


async def post(url, *args, **kwargs):
    return await query(url, "post", *args, **kwargs)
