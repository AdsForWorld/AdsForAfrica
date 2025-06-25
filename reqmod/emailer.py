import base64
from email.message import EmailMessage
import os.path
from datetime import datetime as dt

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def credentials():
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
      
    return creds
  
  
def sendemail(creds, title, body, sendto, issuer, reqby, reason, sendfrom="adsforworldproject+adsforafrica@gmail.com"):
  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    
    message.set_content(f"""
{body}
This is an automated message, please do not reply to this email.
if you believe you aren't the intended recipient of this email, please ignore this message.
--email issuer: {issuer}, requestedby: {reqby}, reason: '{reason}', date: {dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}--
                        """)

    message["To"] = sendto
    message["From"] = sendfrom
    message["Subject"] = title

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


if __name__ == "__main__":
  creds = credentials()
  sendemail(creds, "Automated draft", "This is an automated message")