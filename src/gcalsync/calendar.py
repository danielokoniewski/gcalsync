# wrapper for the google calendar api
# https://developers.google.com/workspace/calendar/api/guides/overview
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarAPIClient(object):
    """
    A client for interacting with the Google Calendar API.
    """

    def __init__(self, creds):
        """
        Initialize the CalendarAPIClient with credentials.

        :param creds: Google API credentials
        """
        self.creds = creds
        self.service = build("calendar", "v3", credentials=creds)

    def create_calendar(self, calendar_name) -> str | None:
        try:
            # If not found, create a new calendar
            new_calendar = {
                "summary": calendar_name,
                "timeZone": "Europe/Berlin",  # Set your desired timezone
            }
            created_calendar = (
                self.service.calendars().insert(body=new_calendar).execute()
            )
            print(f"Created new calendar: {created_calendar['summary']}")
            created_calendar_id = created_calendar.get("id", "")
            return created_calendar_id

        except HttpError as e:
            print(e)
            return None

    def get_calendar_by_name(self, calendar_name) -> str | None:
        """
        fetch the calendar by name. if it does not exist create it
        returns the calendar id if found or created, otherwise None.
        """
        try:
            # the primary calendar has another id but is referenced as "primary" in the api
            if calendar_name == "primary":
                return "primary"

            # Fetch the calendar list
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])

            calendar_id = ""
            # Check if the calendar already exists
            for calendar in calendars:
                if calendar["summary"] == calendar_name:
                    calendar_id = calendar.get("id", "")
                    print(f"Calendar '{calendar_name}' already exists.")
                    return calendar_id

        except HttpError as err:
            print(f"An error occurred: {err}")
            return None

    def insert_event(self, calendar_id, event):
        """
        Create an event in the calendar, must be set using get_calendar_by_name first.

        :param event: The event data to be created.
        :return: The created event or None if an error occurs.
        """
        try:
            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )
            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as err:
            if err.resp.status == 409:
                print("Event already exists, skipping creation.")
                return None
            print(f"An error occurred while creating the event: {err}")
            raise err from HttpError
