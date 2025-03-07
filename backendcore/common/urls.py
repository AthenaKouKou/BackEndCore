import os

FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL',
                                   'https://www.datamixmaster.com/')
TEST_FRONTEND_URL = os.environ.get('TEST_FRONTEND_URL', '')
