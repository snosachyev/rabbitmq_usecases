import csv
import functools
import logging
import pickle
import threading
from copy import copy
from pathlib import Path

from consumer.work_queues_use_case import WorkQueuesCase
from core.rbq import QUEUE_NAME


class WriteToCSVWorkQueuesCase(WorkQueuesCase):
    queue = QUEUE_NAME

    def _write_to_csv(self, filename, message: dict, tlock: threading.Lock):
        """Write to a CSV file in a thread-safe manner"""
        tlock.acquire()
        with open(filename, "a", ) as f:
            writer = csv.DictWriter(f, fieldnames=message.keys())
            # Write the headers only when the write pointer is at 0, aka a new file.
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(message)
        tlock.release()

    def _do_work(self, channel, delivery_tag, body, tlock: threading.Lock):
        """Deserialize the message and write to CSV file."""
        message = pickle.loads(body)

        # The thread ID may get recycled when a thread exits and another is created,
        # so it's not a good indicator of how many threads have been used
        # https://docs.python.org/3/library/threading.html#threading.get_ident
        thread_id = threading.get_ident()

        logging.info(
            f"Active threads: {threading.active_count()} Thread id: {thread_id} Delivery tag: {delivery_tag} Message: {message}")

        data = message.pop("data")
        msg_to_csv = copy(message)
        msg_to_csv["license_id"] = data["license_id"]

        for pred in data["preds"]:
            # Each item in preds should have its own row in the CSV file,
            # so overwrite the same keys for only items in pred.
            msg_to_csv["image_frame"] = pred["image_frame"]
            msg_to_csv["prob"] = pred["prob"]
            msg_to_csv["tags"] = pred["tags"]
            self._write_to_csv(Path("data/data.csv"), msg_to_csv, tlock)

        cb = functools.partial(self._ack_message, channel, delivery_tag)
        channel.connection.add_callback_threadsafe(cb)
