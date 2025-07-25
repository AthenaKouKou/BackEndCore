from typing import NoReturn

from backendcore.common.clients import get_sales_email

from backendcore.emailer.api_send import send_mail


def add_contact_to_db(email: str,
                      subject: str,
                      message: str,
                      project: str = None,
                      ) -> NoReturn:
    """
    Logs the fact that someone reached out to sales.
    """
    return False


def send_contact_email(email: str,
                       subject: str,
                       message: str,
                       project: str = None,
                       ) -> NoReturn:
    """
    Sends the information provided by the sender to the backend client's
    sales email.
    """
    to_email = get_sales_email()
    resp = send_mail(to_emails=to_email,
                     subject=subject,
                     content=message,
                     reply_email=email)
    return resp


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
    send_contact_email(email, subject, message, project)
    add_contact_to_db(email, subject, message, project)
