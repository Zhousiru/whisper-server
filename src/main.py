import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, File, Request
from faster_whisper import WhisperModel
from sse_starlette import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

from args import parse_args
from tasks import TaskOptions, TaskManager
from utils import check_lang_code, response

if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    uvicorn.run("main:app", host=args.host, port=args.port, workers=1,
                log_level="info", reload=(os.getenv("DEBUG") == "1"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")
    args = parse_args()

    logger.info("Loading model...")
    app.state.model = WhisperModel(args.model, device=args.device,
                                   compute_type=args.type)
    logger.info("Model loaded.")

    app.state.msg_queue = asyncio.Queue[str]()
    app.state.task_manager = TaskManager(app.state.model, app.state.msg_queue)

    yield

    app.state.task_manager.cancel_all()
    del app.state.model


app = FastAPI(lifespan=lifespan)

allow_origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/monitor")
async def monitor(request: Request):
    async def streamer():
        while True:
            if await request.is_disconnected():
                break
            yield await app.state.msg_queue.get()

    return EventSourceResponse(streamer())


@app.post("/add-task")
async def add_task(name: str, file: Annotated[bytes, File()], lang: Optional[str] = None, prompt: Optional[str] = None, vad: bool | str = True):
    lang = lang or None

    try:
        check_lang_code(lang)
        options = TaskOptions(file, lang, prompt, vad)
        app.state.task_manager.add(name, options)
        return response("ok")
    except ValueError as e:
        return response("error", str(e))


@app.get("/cancel-task")
async def cancel_task(name: str):
    app.state.task_manager.cancel(name)
    return response("ok")
