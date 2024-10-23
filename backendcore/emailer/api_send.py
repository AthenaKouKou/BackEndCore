import os
import base64
from pathlib import Path

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    FileContent,
    FileName,
    Mail,
    ReplyTo,
)

DEF_SENDER = 'support@datamixmaster.com'


def encode_file(file: str):
    with open(file, 'rb') as f:
        data = f.read()
        f.close()
    return base64.b64encode(data)


def get_attachment(file: str):
    return Attachment(
        FileContent(encode_file(file)),
        FileName(Path(file).name)
    )


def send_mail(to_emails: str, subject: str, content: str,
              from_email: str = DEF_SENDER, reply_email: str = None,
              file: str = None):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=content)

    if reply_email:
        message.reply_to = ReplyTo(reply_email)

    # note: file is actually the file path
    if file:
        message.attachment = get_attachment(file)

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
