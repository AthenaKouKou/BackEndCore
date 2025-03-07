"""
Code to send a password reset email.
"""

import os

import backendcore.common.names as cnm
import backendcore.common.urls as urls

import backendcore.emailer.smtp_send as sm
import backendcore.emailer.api_send as am

# right now, the mail method should be SMTP or API
SMTP = 'smtp'
API = 'api'
VALID_MAIL_METHODS = [SMTP, API]
MAIL_METHOD = os.getenv('MAIL_METHOD', API)
PW_RESET_SENDER = os.getenv('PW_RESET_SENDER')
PW_RESET_SENDER_PW = os.getenv('PW_RESET_SENDER_PW')
SMTP_SERV_HOST = os.getenv('SMTP_SERV_HOST')
SMTP_USER_NAME = os.getenv('SMTP_USER_NAME')

RESET = 'reset_password'
BASE_URL = f'{urls.FRONTEND_BASE_URL}'
TEST_URL = f'{urls.TEST_FRONTEND_URL}'
PW_RES_SUBJ = f'Reset Your {cnm.OUR_NAME} password'


def is_valid_mail_method(method):
    return method in VALID_MAIL_METHODS


def set_base_url(testing_env):
    print(f'{testing_env=}')
    if testing_env:
        base_url = TEST_URL
    else:
        base_url = BASE_URL
    if not base_url.endswith('/'):
        base_url += '/'
    base_url += RESET
    print(f'{base_url=}')
    return base_url


def send_pw_reset(
        reset_tok: str,
        user_email: str,
        tok_ttl_seconds: int,
        method=MAIL_METHOD,
        testing_env=False,
):
    base_url = set_base_url(testing_env)
    if not reset_tok:
        raise ValueError(f'In send_pw_reset, no reset token: {reset_tok=}')
    if not is_valid_mail_method(method):
        raise ValueError(f'Bad mail method: {method}')
    tok_ttl_minutes = tok_ttl_seconds // 60
    MESSAGE = f"""
<p>
  Hello,
</p>

<p>
  We recently received a request to reset your account password. Follow
  the link below to reset it. The link will expire after {tok_ttl_minutes}
  minutes.
</p>

<p>
  <a href="{base_url}?id={user_email}&pw_reset_token={reset_tok}">
  Click here to reset your password.
  </a>
</p>

<p>
- The DataMixMaster Team
</p>
"""
    print('Sending password reset email.')
    if method == SMTP:
        print('Using SMTP to send password reset email')
        if not PW_RESET_SENDER_PW:
            raise ValueError('In send_pw_reset, no sender pw: '
                             + f'{PW_RESET_SENDER_PW=}')
        return sm.send_mail(smtp_serv_host=SMTP_SERV_HOST,
                            sender=PW_RESET_SENDER,
                            sender_pw=PW_RESET_SENDER_PW, subject=PW_RES_SUBJ,
                            recipients=[user_email],
                            html_body=MESSAGE)
    else:
        print('Using API to send password reset email')
        return am.send_mail(to_emails=user_email, subject=PW_RES_SUBJ,
                            content=MESSAGE)
