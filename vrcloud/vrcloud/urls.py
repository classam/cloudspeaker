from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings

from dashboard.views import login
from status.views import status

urlpatterns = [
    url(r'^status$', status, name='status'),
    url(r'^login$', login, name='login'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
