import pika, sys, os, time
#from send import email
import logging
from send import gmail
from lib import setlogger

logger = logging.getLogger(__name__)
level = os.environ.get("LOGGING")
level =  "ERROR" if not level else level
logging.basicConfig(level=setlogger.str_to_log_level(level))

def main():
    # rabbitmq connection
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    except Exception as e:
        logger.error('RabbitMQ connection error:', e)
        sys.exit(0)
    
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = gmail.notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback
    )

    logger.info("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
