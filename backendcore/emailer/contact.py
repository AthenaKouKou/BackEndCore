from typing import NoReturn


def process_contact_form(email: str,
                         subject: str,
                         message: str,
                         project: str = None,
                         ) -> NoReturn:
    """
    Creates an entry in the database for the contact request, then sends an
    email to the designated client's mailing address.
    Email, subject and message fields are mandatory, whereas project is
    optional.
    """
    if not email:
        raise ValueError("No email provided.")
    elif not subject:
        raise ValueError("No subject provided.")
    elif not message:
        raise ValueError("No message provided.")
