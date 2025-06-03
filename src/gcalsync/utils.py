from datetime import datetime

from gcalsync import people


_BIRTHDAY_PREFIX = "b"


def get_event_from_person(
    person: people.Person, birthday_type: bool = False
) -> dict | None:
    """
    Convert a Person object to a Google Calendar event dictionary.

    event settings:
        + https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
        + https://developers.google.com/workspace/calendar/api/v3/reference/events#recurrence
        + https://developers.google.com/workspace/calendar/api/guides/event-typ
    :param person: Person object containing name and birthday.
    :param birthday_type: sets the eventType to "birthday", use only with calendar "primary".
    :return: Dictionary representing the Google Calendar event.
    """
    if not person.birthday:
        return None

    recurrence_rule = "RRULE:FREQ=YEARLY"
    if person.birthday.month == 2 and person.birthday.day == 29:
        # Handle leap year birthdays
        recurrence_rule = "RRULE:FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=-1"

    event = {
        "id": f"{_BIRTHDAY_PREFIX}{person.contact.replace('people/', '')}",
        "summary": f"Birthday: {person.name}",
        "start": {
            "date": person.birthday.strftime("%Y-%m-%d"),
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "date": person.birthday.strftime("%Y-%m-%d"),
            "timeZone": "Europe/Berlin",
        },
        "visibility": "private",
        "transparency": "transparent",
        "recurrence": [recurrence_rule],
    }

    if birthday_type:
        event.update(
            {
                "summary": f"{person.name}",
                "eventType": "birthday",
                "birthdayProperties": {
                    "type": "birthday",
                },
            }
        )
    else:
        event.update(
            {
                "extendedProperties": {
                    "private": {
                        "contact": person.contact,
                        "person_name": person.name,
                        "created_by": "gcalsync",
                        "created_at": datetime.now().isoformat(),
                    }
                }
            }
        )

    return event
