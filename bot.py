from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone must contain exactly 10 digits."
            )

        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except (ValueError, TypeError):
            raise ValueError(
                "Invalid date format. Use DD.MM.YYYY"
            )

        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        found_phone = self.find_phone(phone)

        if found_phone is not None:
            self.phones.remove(found_phone)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        found_phone = self.find_phone(old_phone)

        if found_phone is None:
            raise ValueError("Phone number not found.")

        new_phone = Phone(new_phone)
        found_phone.value = new_phone.value

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item

        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(
            phone.value for phone in self.phones
        )

        birthday = (
            self.birthday.value
            if self.birthday is not None
            else "Not specified"
        )

        return (
            f"Contact: {self.name.value}, "
            f"phones: {phones or 'None'}, "
            f"birthday: {birthday}"
        )


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            try:
                next_birthday = birthday.replace(
                    year=today.year
                )
            except ValueError:
                next_birthday = date(today.year, 2, 28)

            if next_birthday < today:
                try:
                    next_birthday = birthday.replace(
                        year=today.year + 1
                    )
                except ValueError:
                    next_birthday = date(
                        today.year + 1, 2, 28
                    )

            if today <= next_birthday <= today + timedelta(days=7):
                congratulation_day = next_birthday

                if congratulation_day.weekday() == 5:
                    congratulation_day += timedelta(days=2)

                elif congratulation_day.weekday() == 6:
                    congratulation_day += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "birthday": congratulation_day.strftime(
                        "%d.%m.%Y"
                    )
                })

        return sorted(
            upcoming,
            key=lambda item: datetime.strptime(
                item["birthday"], "%d.%m.%Y"
            ).date()
        )

    def __str__(self):
        if not self.data:
            return "Address book is empty."

        return "\n".join(
            str(record) for record in self.data.values()
        )


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter the required arguments."
        except KeyError as e:
            return str(e.args[0])
        except ValueError as e:
            return str(e)

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args

    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)

    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args

    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.edit_phone(old_phone, new_phone)

    return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)

    if record is None:
        return "Contact not found."

    if not record.phones:
        return f"No phone numbers for {name}."

    phones = "; ".join(
        phone.value for phone in record.phones
    )

    return f"{name}: {phones}"


@input_error
def show_all(book: AddressBook):
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args

    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_birthday(birthday)

    return f"Birthday added for {name}: {birthday}"


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)

    if record is None:
        return "Contact not found."

    if record.birthday is None:
        return f"Birthday for {name} is not specified."

    return (
        f"{name}'s birthday: "
        f"{record.birthday.value}"
    )


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    lines = ["Upcoming birthdays:"]

    for item in upcoming:
        lines.append(
            f"{item['birthday']} — {item['name']}"
        )

    return "\n".join(lines)


def parse_input(user_input):
    parts = user_input.strip().split()

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]

    return command, args


def main():
    book = AddressBook()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print(
                "Invalid command. "
                "Available commands: hello, add, change, "
                "phone, all, add-birthday, show-birthday, "
                "birthdays, close, exit."
            )


if __name__ == "__main__":
    main()
