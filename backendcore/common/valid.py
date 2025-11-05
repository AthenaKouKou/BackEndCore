
"""
Place to see if (generic) inputs are valid.
Things like emails and urls.
NOT things like API records that are DMM specific.
"""

import validators as vd


def is_valid_url(url) -> bool:
    return vd.url(url)


def is_valid_email(email) -> bool:
    return vd.email(email)


def is_number(n) -> bool:
    return isinstance(n, int) or isinstance(n, float)


def main():
    print(f'{is_valid_email("gcallah@mac.com")=}')


if __name__ == '__main__':
    main()
