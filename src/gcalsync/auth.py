# wrapper for google authentication

import os.path

import google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    # read contacts
    "https://www.googleapis.com/auth/contacts.readonly",
    # find calendars
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    # write calendar events
    "https://www.googleapis.com/auth/calendar.events",
    # write calendars
    "https://www.googleapis.com/auth/calendar.calendars",
]


def login() -> Credentials | None:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
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
    except google.auth.exceptions.RefreshError as e:
        print(e)
        print("please delete the token.json file and re run the login command.")

    return creds
