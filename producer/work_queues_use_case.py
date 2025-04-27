import logging
import pickle

from core.config import QUEUE_NAME
from core.use_case import ProducerRequestUseCase, WorkQueuesResponse

from producer.schemas import WorkQueuesRequest


class WorkQueuesCase(ProducerRequestUseCase):
    def _execute(self, channel, request: WorkQueuesRequest) -> WorkQueuesResponse:
        channel.queue_declare(queue=QUEUE_NAME)

        for pred in request.data.preds:
            if pred["prob"] < 0.25:
                pred["tags"].append("low_prob")

        # Convert to dict for easy serialization
        payload_dict = request.dict()

        logging.debug(f"Payload received: {payload_dict}")

        channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=pickle.dumps(payload_dict))
        return WorkQueuesResponse(status='received')
