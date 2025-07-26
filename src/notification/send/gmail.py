from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText # import on top
import base64, os, json
import logging

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

gmail_client_id = os.environ.get('GMAIL_CLIENT_ID')
gmail_secret = os.environ.get('GMAIL_SECRET')
gmail_token = os.environ.get('GMAIL_TOKEN')

def create_message(to: str, subject: str, body: str) -> dict:
    """Create a MIME message for sending an email."""
    mime_text = MIMEText(body)
    mime_text["to"] = to
    mime_text["subject"] = subject
    encoded_mime_text = base64.urlsafe_b64encode(mime_text.as_bytes()).decode("utf-8")
    return {"raw": encoded_mime_text}

def notification(message):

    message = json.loads(message)
    mp3_fid = message["mp3_fid"]

    creds = Credentials(
        None,
        refresh_token=gmail_token,
        client_id=gmail_client_id,
        client_secret=gmail_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    try:
        users_resource =  service.users()
        email_body = create_message(to=message["username"],
                                    subject="MP3 Download",
                                    body=f"mp3 file_id: {mp3_fid} is now ready!")
        users_resource.messages().send(userId="me", body=email_body).execute()
    except Exception as e:
        logger.error(f"Send message to {message["username"]} error")
        logger.error(e)
    else:
        logger.info(f"Send message to {message["username"]} succes")
    finally:
        pass
