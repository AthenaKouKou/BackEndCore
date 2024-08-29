import smtplib
import ssl
import email
import sys

from contextlib import contextmanager


CSV_EXT = '.csv'
SMTP_SERV_PORT = 587


def send_mail(
        smtp_serv_host: str,
        sender: str,
        sender_pw: str,
        subject: str,
        recipients: list,
        html_body: str = None,
        attachment: str = None
):
    with _stmp_conn(smtp_serv_host, sender, sender_pw) as conn:
        _send_mail(
            sender,
            conn,
            html_body,
            attachment,
            subject,
            recipients
        )


def _send_mail(
        sender,
        conn,
        html_body,
        attachment,
        subject,
        recipients
):
    print(f'Sending {subject} to {recipients} ...')
    conn.sendmail(sender, recipients, _build_message(sender,
                                                     attachment,
                                                     html_body,
                                                     subject,
                                                     recipients))


SUBJECT = 'Subject'
FROM = 'From'
TO = 'To'
HTML_CONTENT_SUBTYPE = 'html'


def _build_message(sender, attachment, html_body, subject, recipients):
    msg = email.message.EmailMessage()
    msg[SUBJECT] = subject
    msg[FROM] = sender
    msg[TO] = ",".join(recipients)
    if html_body:
        msg.set_content(html_body, subtype=HTML_CONTENT_SUBTYPE)
    if attachment:
        msg.add_attachment(attachment, filename=slugify(subject) + CSV_EXT)
    return msg.as_string()


def slugify(s: str):
    """
    Lower-cases string and converts spaces and dashes to underscores.
    """
    s = s.lower()
    s = s.replace(" ", "_")
    s = s.replace("-", "_")
    return s


@contextmanager
def _stmp_conn(smtp_serv_host, sender, sender_pw):
    conn = _open_connection(smtp_serv_host)
    conn.login(sender, sender_pw)
    try:
        yield conn
    finally:
        _close_connection(conn)


def _open_connection(smtp_serv_host: str):
    print('Opening SMTP connection ...')
    print(f'{smtp_serv_host=}')
    print(f'{SMTP_SERV_PORT=}')
    conn = smtplib.SMTP(
        smtp_serv_host,
        SMTP_SERV_PORT,
    )
    conn.ehlo()
    conn.starttls(
        context=ssl.create_default_context()
    )
    conn.ehlo()
    return conn


def _close_connection(smtp):
    print('Closing SMTP connection ...')
    smtp.quit()


SMTP_SERV_HOST_IDX = 1
SENDER_IDX = 2
SENDER_PW_IDX = 3
SUBJECT_IDX = 4
RECIPS_IDX = 5
BODY_IDX = 6


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Not enough args')
        sys.exit(1)
    send_mail(
        smtp_serv_host=sys.argv[SMTP_SERV_HOST_IDX],
        sender=sys.argv[SENDER_IDX],
        sender_pw=sys.argv[SENDER_PW_IDX],
        subject=sys.argv[SUBJECT_IDX],
        recipients=sys.argv[RECIPS_IDX].split(','),
        html_body=sys.argv[BODY_IDX]
    )
