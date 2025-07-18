import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from flask import logging
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId


def flask_logger_set (level: str) -> None:

    if 0 == level.find("DEBUG"):
        server.logger.setLevel(logging.logging.DEBUG)
    elif 0 == level.find("INFO"):
        server.logger.setLevel(logging.logging.INFO)
    elif 0 == level.find("WARNING"):
        server.logger.setLevel(logging.logging.WARNING)
    elif 0 == level.find("ERROR"):
        server.logger.setLevel(logging.logging.ERROR)
    elif 0 == level.find("CRITICAL"):
        server.logger.setLevel(logging.logging.CRITICAL)
    else:
        server.logger.setLevel(logging.logging.ERROR)

server = Flask(__name__)

level = os.environ.get("LOGGING")
level =  "ERROR" if not level else level
flask_logger_set(level)

mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# Start RabitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
server.logger.debug(f'RabitMQ channel {channel}')

@server.route("/login", methods=["POST"])
def login():

    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        server.logger.debug(f'token validation error')
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            server.logger.debug(f'exactly 1 file required: {request.files}')
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                server.logger.debug(err)
                return err

        return "success!", 200
    else:
        server.logger.debug(f'authorization error')
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        server.logger.debug(f'token validation error')
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            server.logger.debug(f'fid is required')
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            server.logger.debug(err)
            return "internal server error", 500

    server.logger.debug(f'authorization error')
    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
