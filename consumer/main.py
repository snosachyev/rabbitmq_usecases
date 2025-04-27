import logging
import os
import sys

from consumer.write_csv_work_queues_use_case import WriteToCSVWorkQueuesCase
from consumer.write_fanout_message_work_queues_use_case import WriteFanoutMessageWorkQueuesCase
from consumer.write_message_work_queues_use_case import WriteMessageWorkQueuesCase


def execute():
    WriteMessageWorkQueuesCase().execute()
    WriteToCSVWorkQueuesCase().execute()
    WriteFanoutMessageWorkQueuesCase().execute()

if __name__ == "__main__":
    ch = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=20,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[ch]
    )

    logging.info(f"Starting consumer...")
    consumers = {
        'WriteMessageWorkQueuesCase': WriteMessageWorkQueuesCase,
        'WriteToCSVWorkQueuesCase': WriteToCSVWorkQueuesCase,
        'WriteFanoutMessageWorkQueuesCase': WriteFanoutMessageWorkQueuesCase
    }
    sys.exit(consumers.get(os.environ['CONSUMER'], 'WriteMessageWorkQueuesCase')().execute())
