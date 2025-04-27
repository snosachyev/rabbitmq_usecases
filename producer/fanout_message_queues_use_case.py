import logging

from core.config import FANOUT_QUEUE_MESSAGE
from core.use_case import ProducerRequestUseCase, WorkQueuesResponse

from producer.schemas import MessageQueuesRequest


class FanoutMessageQueuesCase(ProducerRequestUseCase):
    queue = FANOUT_QUEUE_MESSAGE

    def _execute(self, channel, request: MessageQueuesRequest) -> WorkQueuesResponse:
        channel.queue_declare(queue=self.queue)
        channel.exchange_declare(exchange='logs', exchange_type='fanout')

        logging.debug(f"Payload received: {request.message}")
        channel.basic_publish(exchange="logs", routing_key='', body=request.message)
        return WorkQueuesResponse(status='received')
