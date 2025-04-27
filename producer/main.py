import logging
import sys
import uvicorn

from fastapi import FastAPI

from producer.fanout_message_queues_use_case import FanoutMessageQueuesCase
from producer.message_queues_use_case import MessageQueuesCase
from producer.schemas import WorkQueuesRequest, MessageQueuesRequest
from producer.work_queues_use_case import WorkQueuesCase


app = FastAPI(title="FastAPI + RabbitMQ + Consumer Demo")

@app.on_event("startup")
async def logging_init():
    """Configure logging to output to stdout and format it for easy viewing"""
    ch = logging.StreamHandler(sys.stdout)
    # Change level to [10, 20, 30, 40, 50] for different severity,
    # where 10 is lowest (debug) and 50 is highest (critical)
    logging.basicConfig(
        level=20,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[ch]
    )
    logging.info(f"Starting producer...")


@app.get("/")
def read_root():
    return {"Developer": "Sergey Nosachyev"}

@app.post("/api")
def accept_payload(request: WorkQueuesRequest):
    WorkQueuesCase().execute(request)
@app.post("/api/message")
def accept_payload(request: MessageQueuesRequest):
    MessageQueuesCase().execute(request)
@app.post("/api/fanout_message")
def accept_payload(request: MessageQueuesRequest):
    FanoutMessageQueuesCase().execute(request)



# for develop
if __name__ == '__main__':
    uvicorn.run(app='main:app',
                host='0.0.0.0',
                port=80,
                reload=True)
