import os, requests
import logging

logger = logging.getLogger('server.sub')

def login(request):
    auth = request.authorization
    if not auth:
        logger.info(f'wrong credentials {request.authorization}')
        return None, ("missing credentials", 401)

    logger.debug(f'request authentication for {request.authorization}') 
    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
    )

    if response.status_code == 200:
        logger.debug(f'authentication success {request.authorization}') 
        return response.text, None
    else:
        logger.info(f'authentication reject {request.authorization}') 
        return None, (response.text, response.status_code)
