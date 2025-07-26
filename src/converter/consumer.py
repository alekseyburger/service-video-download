import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3
import logging
from lib import setlogger

logger = logging.getLogger(__name__)
slevel = os.environ.get("LOGGING")
slevel =  "ERROR" if not slevel else slevel
logging.basicConfig(level=setlogger.str_to_log_level(slevel))

def main():
    client = MongoClient("host.minikube.internal", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    except Exception as e:
        logger.error('RabbitMQ connection error:', e)
        sys.exit(0)

    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.convert_and_msg(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    logger.info("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    main()
