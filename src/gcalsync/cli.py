import fire

from gcalsync import auth, people, calendar, utils

_DEFAULT_CALENDAR_NAME = "contacts"


class Cli(object):
    """
    CLI class to handle command line interface for the gcalsync application.

    This class is used to parse command line arguments and execute the main function of the gcalsync application.
    """

    _creds = None

    def __init__(self):
        """Initialize the CLI class."""
        pass

    def read_contacts(self):
        """
        Reads the contacts from the People API and prints all people with birthday
        """

        if not self.logged_in:
            self.login()
        for person in people.PeopleAPIClient(self._creds).get_birthdays():
            print(f"{person}")

    def sync_contacts(self, calendar_name=_DEFAULT_CALENDAR_NAME):
        """Method to sync contacts."""
        print("Syncing contacts...")
        if not self.logged_in:
            self.login()

        use_birthday_type: bool = True if calendar_name == "primary" else False

        p = people.PeopleAPIClient(self._creds)
        c = calendar.CalendarAPIClient(self._creds)
        cal_id = c.get_calendar_by_name(calendar_name)
        if not cal_id:
            print("calendar does not exists - trying to create it")
            c.create_calendar(calendar_name)

        if not cal_id:
            print(f"Could not find or create calendar with name {calendar_name}.")
            return

        for person in p.get_birthdays(10):
            print(f"Syncing contact: {person}")
            if person.birthday:
                event = utils.get_event_from_person(person, use_birthday_type)
                if event:
                    print(f"Creating event for {person.name} on {person.birthday}")
                    c.insert_event(cal_id, event)
                else:
                    print(f"No birthday found for {person.name}, skipping.")
                    continue

    def get_calendar_by_name(self, name="contacts"):
        """Method to get calendar by name."""
        print("Getting calendar by name...")
        if not self.logged_in:
            self.login()
        cal_id = calendar.CalendarAPIClient(self._creds).get_calendar_by_name(name)
        if cal_id:
            print(f"Calendar found for name {name}: {cal_id}")
        else:
            print("Calendar not found")

    def login(self):
        """Method to handle user login."""
        print("Logging in...")
        self._creds = auth.login()

    @property
    def logged_in(self):
        """Property to check if the user is logged in."""
        return True if self._creds else False


def main():
    """
    cli entrypoint for the main execution of the program.

    uses fire to handle command line arguments and execute the main function.
    """
    fire.Fire(Cli)


if __name__ == "__main__":
    """Run the main function when the script is executed."""
    main()
