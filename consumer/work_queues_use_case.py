import functools
import logging
import threading

from core.use_case import ConsumerUseCase



class WorkQueuesCase(ConsumerUseCase):
    tlock: threading.Lock = threading.Lock()

    def _ack_message(self, channel, delivery_tag):
        """Note that `channel` must be the same pika channel instance via which
        the message being ACKed was retrieved (AMQP protocol constraint).
        """
        if channel.is_open:
            logging.info(f"delivery_tag: {delivery_tag}")
            channel.basic_ack(delivery_tag)
        else:
            # Channel is already closed, so we can't ACK this message;
            # log and/or do something that makes sense for your app in this case.
            pass

    def _callback(self, channel, method_frame, _header_frame, body, args):
        """The callback function when a new message is received"""
        threads, tlock = args
        tlock.acquire()
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target=self._do_work, args=(channel, delivery_tag, body, tlock))
        t.start()
        threads.append(t)
        tlock.release()

    def _execute(self, channel):

        # Wait for all to complete
        # Note: may not be called when container is stopped?
        channel.queue_declare(queue=self.queue)
        channel.basic_qos(prefetch_size=0, prefetch_count=10)

        threads = []
        on_message_callback = functools.partial(self._callback, args=(threads, self.tlock))
        channel.basic_consume(queue=self.queue, on_message_callback=on_message_callback)
        channel.start_consuming()

        logging.info(f"Number of threads to join: {len(threads)}")
        for thread in threads:
            thread.join()
