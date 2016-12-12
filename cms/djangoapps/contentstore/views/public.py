"""
Public views
"""
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings

#BharatMooc 
#Date added: 18/08/2014
#Author: MOOC Dev Team
#Date modified : NA 
#Modified by : NA 
#Description : Added State City and Person table in database 
from student.models import (
    Mooc_state,Mooc_city,Mooc_person #######  three tables are added
)
from edxmako.shortcuts import render_to_response

from external_auth.views import (ssl_login_shortcut, ssl_get_cert_from_request,
                                 redirect_with_get)
from microsite_configuration import microsite

__all__ = ['signup', 'login_page', 'howitworks']


@ensure_csrf_cookie
def signup(request):
    """
    Display the signup form.
    """
    csrf_token = csrf(request)['csrf_token']
    if request.user.is_authenticated():
        return redirect('/course/')
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES_IMMEDIATE_SIGNUP'):
        # Redirect to course to login to process their certificate if SSL is enabled
        # and registration is disabled.
        return redirect_with_get('login', request.GET, False)

    return render_to_response('register.html', {'csrf': csrf_token})


@ssl_login_shortcut
@ensure_csrf_cookie
def login_page(request):
    """
    Display the login form.
    """
    csrf_token = csrf(request)['csrf_token']
    if (settings.FEATURES['AUTH_USE_CERTIFICATES'] and
            ssl_get_cert_from_request(request)):
        # SSL login doesn't require a login view, so redirect
        # to course now that the user is authenticated via
        # the decorator.
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect('/course/')
    if settings.FEATURES.get('AUTH_USE_CAS'):
        # If CAS is enabled, redirect auth handling to there
        return redirect(reverse('cas-login'))

    return render_to_response(
        'login.html',
        {
            'csrf': csrf_token,
            'forgot_password_link': "//{base}/login#forgot-password-modal".format(base=settings.LMS_BASE),
            'platform_name': microsite.get_value('platform_name', settings.PLATFORM_NAME),
        }
    )
#BharatMooc 
#Date added: 18/08/2014
#Author: MOOC Dev Team
#Date modified : NA 
#Modified by : NA 
#Description : Added State and City  in Database
@ensure_csrf_cookie
def signup(request):
    """
    Display the signup form.
    """
    states=Mooc_state.objects.all() 
    city = Mooc_city.objects.all() 
    csrf_token = csrf(request)['csrf_token']
    if request.user.is_authenticated():
        return redirect('/course')
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES_IMMEDIATE_SIGNUP'):
        # Redirect to course to login to process their certificate if SSL is enabled
        # and registration is disabled.
        return redirect(reverse('login'))

    return render_to_response('register.html', {'csrf': csrf_token ,'states':states,'cities':city})


def howitworks(request):
    "Proxy view"
    if request.user.is_authenticated():
        return redirect('/home/')
    else:
        return render_to_response('howitworks.html', {})
