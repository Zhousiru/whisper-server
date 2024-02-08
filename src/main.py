import io
import os
import json
import logging
import sys
from typing import Annotated, Optional
from faster_whisper import WhisperModel
from sse_starlette import EventSourceResponse
import uvicorn
from fastapi import FastAPI, File, Request
from args import parse_args
from contextlib import asynccontextmanager


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

    yield

    del app.state.model


app = FastAPI(lifespan=lifespan)


@app.post("/transcribe")
async def transcribe(request: Request, file: Annotated[bytes, File()], lang: Optional[str] = None, prompt: Optional[str] = None, vad: bool = True):
    async def transcribe_streamer():
        segments, info = app.state.model.transcribe(
            io.BytesIO(file), language=lang, initial_prompt=prompt, vad_filter=vad)

        if (lang == None):
            yield json.dumps({"type": "language detection", "data": info.language})

        for s in segments:
            if await request.is_disconnected():
                break
            yield json.dumps({"type": "transcription", "data": {"start": s.start, "end": s.end, "text": s.text}})

    return EventSourceResponse(transcribe_streamer())
