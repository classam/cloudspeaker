from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import Signer
from django.core.urlresolvers import reverse


def verification_email_message(email, verification_url):
    """
    Return the message that we send to the user.
    """
    return settings.VERIFICATION_EMAIL.format(email=email,
                                              site_title=settings.SITE_TITLE,
                                              verification_url=verification_url)


def verification_email(user):
    """
    Send a verification email to the user.
    """
    signer = Signer()
    verification_signature = signer.sign(user.email)
    from .views import verify
    verification_url = settings.SITE_URL + reverse(verify, kwargs={'signature':verification_signature})

    send_mail(subject=settings.VERIFICATION_EMAIL_SUBJECT,
              message=verification_email_message(user.email, verification_url),
              from_email=settings.SERVER_EMAIL,
              recipient_list=[user.email])


def password_recovery_email(user):
    """
    Send a password recovery email to the user.
    """
    pass