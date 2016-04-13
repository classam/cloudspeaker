import logging

from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .emails import verification_email
from .forms import RegistrationForm
from .models import Profile


log = logging.getLogger('vrcloud.{}'.format(__name__))


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
                                     "Your account has been disabled.")
        else:
            potential_user = User.objects.filter(email=username)
            if len(potential_user) == 1:
                user = authenticate(username=potential_user[0].username, password=password)
                if user is not None:
                    if user.is_active:
                        auth_login(request, user)
                        return HttpResponseRedirect(settings.LOGIN_LANDING_PAGE)
                    else:
                        messages.add_message(request, messages.ERROR,
                                             "Your account has been disabled.")
                else:
                    messages.add_message(request, messages.ERROR,
                                         'Authentication failed!')
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
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password_again = form.cleaned_data['password_again']
            email = form.cleaned_data['email']

            if password != password_again:
                messages.add_message(request, messages.ERROR,
                                     "Your password didn't match both times!")
            elif len(User.objects.filter(email=email)) > 0:
                messages.add_message(request, messages.ERROR,
                                     "A user already exists with that e-mail address.")
            else:
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    user = authenticate(username=username, password=password)
                    verification_email(user)
                    auth_login(request, user)
                    p = Profile(user=user)
                    p.save()
                    log.info("Successfully created user {}".format(user.username))
                    return HttpResponseRedirect(settings.LOGIN_LANDING_PAGE)
                except IntegrityError as e:
                    messages.add_message(request, messages.ERROR,
                                         "A user with that username already exists.")
    else:
        form = RegistrationForm()
    return render(request, "dashboard/register.html", {'form':form})


def verify(request, signature):
    """
    Check that the email hash is good.
    If so, set user.profile.email_verified to True
    """
    log.info("Signature: '{}'".format(signature))
    signer = signing.Signer()
    try:
        email = signer.unsign(signature)
        log.info("Email unsigned {}".format(email))
        user = User.objects.get(email=email)
        if user.is_active:
            user.profile.email_verified = True
            user.profile.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Email verified! Great job!")
            if request.user:
                return HttpResponseRedirect(settings.LOGIN_LANDING_PAGE)
            else:
                return HttpResponseRedirect(settings.HOME_PAGE)
        else:
            message = "Your account has been disabled!"
            return render(request, "dashboard/error.html", {'message': message})
    except signing.BadSignature:
        message = "Signing error!"
        return render(request, "dashboard/error.html", {'message': message})
    except ObjectDoesNotExist:
        message = "User does not exist!"
        return render(request, "dashboard/error.html", {'message': message})


def logout(request):
    """
    I think you already know what logout does.
    """
    auth_logout(request)
    return HttpResponseRedirect(settings.HOME_PAGE)


def send_password_recovery(request):
    """

    """
    return


def send_verification_email(request):
    """

    """
    return
