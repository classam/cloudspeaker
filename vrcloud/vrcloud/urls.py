from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings

from dashboard.views import login, register, verify
from dashboard.views import logout
from status.views import status

urlpatterns = [
    url(r'^status$', status),
    url(r'^login$', login),
    url(r'^register$', register),
    url(r'^logout$', logout),
    url(r'^verify/(?P<signature>.*)$', verify),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
