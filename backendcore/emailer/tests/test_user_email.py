import backendcore.emailer.user_email as em


def test_email_normalization():
    assert em.NORM_EMAIL == em.normalize_email(em.TEST_EMAIL)
    assert em.NORM_EMAIL == em.normalize_email(em.NORM_EMAIL)
