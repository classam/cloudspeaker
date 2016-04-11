from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings

from status.views import status

urlpatterns = [
    url(r'^status$', status, name='status'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
