import jwt, datetime, os
from flask import Flask, request
from flask import logging
from flask_mysqldb import MySQL
from lib import setlogger

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

jwt_secret = os.environ.get("JWT_SECRET")

slevel = os.environ.get("LOGGING")
slevel =  "ERROR" if not slevel else slevel
server.logger.setLevel(level=setlogger.str_to_log_level(slevel))

server.logger.info(f'Start server with MySql credentials: {server.config["MYSQL_USER"]}@' +
    f'{server.config["MYSQL_HOST"]} DB: {server.config["MYSQL_DB"]} ' +
    f'port: {server.config["MYSQL_PORT"]}')

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    # auth.username = "user@email.com"
    # auth.password = "user"
    if not auth:
        server.logger.debug(f'there is no auth field in request')
        return "missing credentials", 401

    server.logger.debug(f'authentication request for user: {auth}')
    # check db for username and password
    try:
        cur = mysql.connection.cursor()
        res = cur.execute(
            "SELECT email, password FROM user WHERE email=%s", (auth.username,)
        )
    except Exception as e:
        server.logger.info(e)
        return "MySql Server Error", 500


    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            # wrong password
            server.logger.debug(f'there are invalid credentials: {auth.username}:{auth.password}')
            return "invalid credentials", 401
        else:
            token = createJWT(auth.username, jwt_secret, True)
            server.logger.info(f'create token for {auth.username} : {token}')
            return token
    else:
        #  user doesn't exist
        server.logger.debug(f'invalid DB result for user {auth.username}')
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        server.logger.debug(f'there is no token in request')
        return "missing credentials", 401

    # string <Barier token>. We need the token
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, jwt_secret, algorithms=["HS256"]
        )
    except Exception as err:
        server.logger.debug(f'token is not valid')
        server.logger.debug(err)
        return "not authorized", 403

    server.logger.info(f'token is valid')
    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(datetime.UTC),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
