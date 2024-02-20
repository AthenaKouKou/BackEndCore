import backendcore.email.user_email as em

def test_email_normalization():
   assert em.NORM_EMAIL == em.normalize_email(em.TEST_EMAIL) 
