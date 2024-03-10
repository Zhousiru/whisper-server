import asyncio
import json
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from faster_whisper import WhisperModel

from utils import to_async_iterable


@dataclass
class TaskOptions:
    file: bytes
    lang: Optional[str]
    prompt: Optional[str]
    vad: bool


@dataclass
class TaskRecord:
    task_name: str
    task: asyncio.Task


class TaskManager:
    tasks: list[TaskRecord]
    model: WhisperModel
    msg_queue: asyncio.Queue[str]
    maxiumum_tasks: int

    def __init__(self, model: WhisperModel, msg_queue: asyncio.Queue, maximum_tasks: int = 1):
        self.tasks = []
        self.model = model
        self.msg_queue = msg_queue
        self.maximum_tasks = maximum_tasks

    def add(self, task_name: str, options: TaskOptions):
        if (len(self.tasks) >= self.maximum_tasks):
            raise ValueError("Maximum tasks reached")
        if (task_name in [record.task_name for record in self.tasks]):
            raise ValueError("Task name already exists")

        task = asyncio.create_task(self.run_task(task_name, options))
        self.tasks.append(TaskRecord(task_name, task))

    def cancel(self, task_name: str):
        for record in self.tasks:
            if (record.task_name == task_name):
                record.task.cancel()
                self.tasks.remove(record)
                self.msg_queue.put_nowait(json.dumps(
                    {
                        "taskName": task_name,
                        "type": "status",
                        "data": "canceled"
                    }
                ))
                break

    def cancel_all(self):
        for record in self.tasks:
            record.task.cancel()
            self.msg_queue.put_nowait(json.dumps(
                {
                    "taskName": record.task_name,
                    "type": "status",
                    "data": "canceled"
                }
            ))
        self.tasks.clear()

    async def run_task(self, task_name: str, options: TaskOptions):
        self.msg_queue.put_nowait(json.dumps(
            {
                "taskName": task_name,
                "type": "status",
                "data": "init"
            }
        ))

        segments, info = await asyncio.to_thread(
            self.model.transcribe,
            BytesIO(options.file),
            language=options.lang,
            initial_prompt=options.prompt,
            vad_filter=options.vad
        )

        self.msg_queue.put_nowait(json.dumps(
            {
                "taskName": task_name,
                "type": "status",
                "data": "start"
            }
        ))

        if (options.lang == None):
            self.msg_queue.put_nowait(json.dumps(
                {
                    "taskName": task_name,
                    "type": "language-detection",
                    "data": info.language
                }
            ))

        async for s in to_async_iterable(segments):
            self.msg_queue.put_nowait(json.dumps(
                {
                    "taskName": task_name,
                    "type": "transcription",
                    "data": {
                        "start": s.start,
                        "end": s.end,
                        "text": s.text
                    }
                }
            ))

        self.msg_queue.put_nowait(json.dumps(
            {
                "taskName": task_name,
                "type": "status",
                "data": "done"
            }
        ))

        for record in self.tasks:
            if (record.task_name == task_name):
                self.tasks.remove(record)
