import logging

from core.config import QUEUE_MESSAGE
from core.use_case import ProducerRequestUseCase, WorkQueuesResponse

from producer.schemas import MessageQueuesRequest


class MessageQueuesCase(ProducerRequestUseCase):
    queue = QUEUE_MESSAGE

    def _execute(self, channel, request: MessageQueuesRequest) -> WorkQueuesResponse:
        channel.queue_declare(queue=self.queue)
        logging.debug(f"Payload received: {request.message}")
        channel.basic_publish(exchange="", routing_key=self.queue, body=request.message)
        return WorkQueuesResponse(status='received')
