import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, ReplyTo)

DEF_SENDER = 'support@datamixmaster.com'


def send_mail(to_emails: str, subject: str, content: str,
              from_email=DEF_SENDER, reply_email: str = None):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=content)

    if reply_email:
        message.reply_to = ReplyTo(reply_email)

    try:
        print('About to send pw rest email using API key.')
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        # for debugging:
        # print(response.body)
        # print(response.headers)
        return response.status_code
    except Exception as e:
        print(str(e))
        return None


def main():
    send_mail(to_emails='gcallah@mac.com', subject='Test Send',
              content='Test content.')


if __name__ == '__main__':
    main()
