def normalize_email(email):
    """
    We are assuming emails are case insensitive, so all this does is
    lowercase them
    """
    return email.lower()


TEST_EMAIL = 'UPPER@test.com'
NORM_EMAIL = 'upper@test.com'
