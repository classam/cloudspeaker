from django.conf.urls import include, url

from status.views import status

urlpatterns = [
    url(r'^status$', status, name='status'),
]
