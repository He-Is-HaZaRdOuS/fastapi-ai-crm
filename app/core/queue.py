import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.note import summarize_note

queue = asyncio.Queue()
in_flight = set()

executor = ThreadPoolExecutor(max_workers=2)


class Job:
    def __init__(self, note_id: int, retries: int = 0):
        self.note_id = note_id
        self.retries = retries


def enqueue_job(note_id: int):
    if note_id not in in_flight:
        in_flight.add(note_id)
        queue.put_nowait(Job(note_id))


async def worker():
    while True:
        job: Job = await queue.get()
        try:
            # run blocking summarize_note in a thread
            await asyncio.get_event_loop().run_in_executor(
                executor, summarize_note, job.note_id
            )
        except Exception as e:
            print(f"Job {job.note_id} failed")
        finally:
            in_flight.discard(job.note_id)
            queue.task_done()


def get_queue():
    return queue


async def start_workers(num_workers: int = 2):
    tasks = [asyncio.create_task(worker()) for _ in range(num_workers)]
    return tasks
