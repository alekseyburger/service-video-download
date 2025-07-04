import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))
jwt_secret = os.environ.get("JWT_SECRET")

print("config:", server.config["MYSQL_HOST"], server.config["MYSQL_USER"],
    server.config["MYSQL_PASSWORD"],
    server.config["MYSQL_DB"],
    server.config["MYSQL_PORT"])

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    # auth.username = "user@email.com"
    # auth.password = "user"
    if not auth:
        print("there is no auth field in request")
        return "missing credentials", 401

    print("credentials: ", auth)
    # check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            # wrong password
            print("invalid credentials: ", auth.username,auth.password)
            return "invalid credentials", 401
        else:
            token = createJWT(auth.username, jwt_secret, True)
            print("token:", token)
            return token
    else:
        #  user doesn't exist
        print("invalid DB result")
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    # string <Barier token>. We need the token
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, jwt_secret, algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
