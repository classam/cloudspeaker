from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect

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
    """
    return {}

def recover(request):
    """

    """
    return {}

def verify(request, hmac):
    """

    """
    return {}
