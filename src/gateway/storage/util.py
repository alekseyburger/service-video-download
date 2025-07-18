import pika, json
import logging

logger = logging.getLogger('server.sub')

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        logger.error(f'can\'t write video to file system')
        logger.error(err)
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        logger.debug(f'send message with video {str(fid)}')
    except Exception as err:
        logger.error(f'can\'t send message with video {str(fid)}')
        logger.error(err)
        fs.delete(fid)
        return "internal server error", 500
