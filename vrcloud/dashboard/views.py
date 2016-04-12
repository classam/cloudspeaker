from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core import signing

# Create your views here.


def login(request):
    """
    Log a user in!
    """
    if request.POST:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if not username or not password:
            messages.add_message(request, messages.ERROR,
                                 'No username or password provided.')
            return render(request, "dashboard/login.html", {})

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect(settings.LOGIN_LANDING_PAGE)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Your account has been disabled.')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Authentication failed!')

    return render(request, "dashboard/login.html",  {})


def register(request):
    """
    Create a new account!
    This account will be created in an "e-mail unverified" state until the user
    verifies the e-mail.
    """
    return {}


def verify(request, signature):
    """
    Check that the email hash is good.
    If so, give that user the 'can_email' permission.
    """
    signer = signing.Signer()
    try:
        email = signer.unsign(signature)

    except signing.BadSignature:
        messages.add_message(request, messages.ERROR, "Oh no! Something has gone wrong!")


def recover(request):
    """

    """
    return {}


def send_verification_email(request):
    """

    """
    return {}
