import backendcore.emailer.contact as ct


TEST_EMAIL = 'tester@test.com'
TEST_SUBJECT = 'fake subject'
TEST_MESSAGE = 'fake message'
TEST_PROJECT = 'fake project'


def test_process_contact_form():
    # Empty test, TODO
    ct.process_contact_form(TEST_EMAIL, TEST_SUBJECT, TEST_MESSAGE,
                            TEST_PROJECT)
