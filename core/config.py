import pika

QUEUE_NAME = 'csv_queue'
QUEUE_MESSAGE = 'message'
FANOUT_QUEUE_MESSAGE = 'fanout_message'

rabbit_params = pika.ConnectionParameters(host="rabbitmq")
