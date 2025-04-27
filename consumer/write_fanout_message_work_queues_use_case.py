import functools
import logging
import threading

from consumer.work_queues_use_case import WorkQueuesCase
from core.rbq import FANOUT_QUEUE_MESSAGE


class WriteFanoutMessageWorkQueuesCase(WorkQueuesCase):
    queue = FANOUT_QUEUE_MESSAGE

    @staticmethod
    def _send_message(message: str, tlock: threading.Lock):
        """Logging message from queue."""
        thread_id = threading.get_ident()
        tlock.acquire()
        logging.info(
            f"Active threads: {threading.active_count()} Thread id: {thread_id} Message: {message}")
        tlock.release()

    def _do_work(self, channel, delivery_tag, body, tlock: threading.Lock):
        self._send_message(body, tlock)
        cb = functools.partial(self._ack_message, channel, delivery_tag)

        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        channel.queue_declare(queue=self.queue, exclusive=True)
        channel.queue_bind(exchange='logs', queue=self.queue)

        channel.connection.add_callback_threadsafe(cb)
