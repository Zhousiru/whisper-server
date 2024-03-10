import asyncio
from enum import StrEnum
from typing import Literal, Optional


async def to_async_iterable(sync_iterable):
    done = object()
    it = iter(sync_iterable)
    while (value := await asyncio.to_thread(next, it, done)) is not done:
        yield value


def response(status: Literal["ok", "error"], msg: Optional[str] = None):
    return {"status": status, "msg": msg}
