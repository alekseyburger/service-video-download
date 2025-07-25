import pika, json, tempfile, os
from bson.objectid import ObjectId
from moviepy.video.io.VideoFileClip import VideoFileClip
import logging

logger = logging.getLogger(__name__)

def convert_and_msg(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    logger.debug(f'request for {message["video_fid"]} is received')
    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temp video file
    audio = VideoFileClip(tf.name).audio
    tf.close()

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    logger.info(f'converted data {message["video_fid"]} is ready. MP3 {str(fid)}')

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        logger.error(f"Send MP3 {str(fid)} message error")
        logger.error(err)
        fs_mp3s.delete(fid)
        return "failed to publish message"
