# wrapper for the google people api
# https://developers.google.com/people
from typing import Any, Generator

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime


class Person(object):
    def __init__(self, contact, name: str, birthday: datetime = None):
        self.contact = contact
        self.name = name
        self.birthday = birthday

    def __str__(self):
        return f"{self.name} - {self.birthday.strftime('%Y-%m-%d') if self.birthday else 'No Birthday'}"

    def __repr__(self):
        return f"Person(name={self.name}, birthday={self.birthday})"


class Birthday(object):
    """
    Birthday Class
    """

    def __init__(self, date: datetime):
        self.date = date

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

    def __repr__(self):
        return f"Birthday(date={self.date})"


class PeopleAPIClient(object):
    def __init__(self, creds):
        """
        Initialize the PeopleAPIClient with credentials.

        :param creds: Google API credentials
        """
        self.creds = creds
        self.service = build("people", "v1", credentials=creds)

    def get_birthdays(self, page_size=10) -> Generator[Person, Any, list[Any] | None]:
        """
        Fetch birthdays from the People API.

        Todo: use searchContacts instead of connections list to filter by birthday.
        https://developers.google.com/people/api/rest/v1/people/searchContacts

        :return: An iterable of Peoples with birthday dates.
        """
        try:
            print("Fetching birthdays from People API")
            con = self.service.people().connections()
            request = con.list(
                resourceName="people/me",
                pageSize=page_size,
                personFields="names,nicknames,birthdays",
            )
            while request is not None:
                results = request.execute()
                connections = results.get("connections", [])
                yield from self._handle_connection_results(connections)
                request = con.list_next(request, results)

        except HttpError as err:
            print(f"An error occurred: {err}")
            return []

    def _handle_connection_results(
        self, connections: list[dict]
    ) -> Generator[Person, Any, None]:
        for person in connections:
            name = person.get("names", [{}])[0].get("displayName", "No Name")
            if name == "No Name":
                print(f"Skipping person with no name: {person.get('resourceName', '')}")
                continue
            birthdays_data = person.get("birthdays", [])
            if birthdays_data:
                date = birthdays_data[0].get("date", {})
                year = date.get("year", "")
                month = date.get("month", "")
                day = date.get("day", "")
                if year and month and day:
                    birthday_date = datetime(year, month, day)
                    yield Person(
                        contact=person.get("resourceName", ""),
                        name=name,
                        birthday=birthday_date,
                    )
        return None

    def list_people(self, page_size=100):
        """
        Reads people from the People API and prints the names with the birthdays

        Args:
            page_size: size for paging, Default = 100
        """
        try:
            # Call the People API
            print(f"List {page_size} connection names")
            results = (
                self.service.people()
                .connections()
                .list(
                    resourceName="people/me",
                    pageSize=page_size,
                    personFields="names,birthdays,events",
                )
                .execute()
            )
            connections = results.get("connections", [])

            for person in connections:
                names = person.get("names", [])
                birthdays = person.get("birthdays", [])
                events = person.get("events", [])
                name, birthday, event = (None, None, None)

                if names:
                    name = names[0].get("displayName", "No Name")
                if birthdays:
                    birthday = datetime(
                        birthdays[0].get("date", {}).get("year", ""),
                        birthdays[0].get("date", {}).get("month", ""),
                        birthdays[0].get("date", {}).get("day", ""),
                    )
                if events:
                    event = events[0].get("date", {}).get("year", "No Event")
                print(f"Name: {name}, Birthday: {birthday}, Event: {event}")

        except HttpError as err:
            print(err)
