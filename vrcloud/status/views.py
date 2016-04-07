from django.shortcuts import render
from django.core.cache import cache

from .models import database_ok, cache_ok, data_ok


def status(request):
    """
    Diagnostics!

    Report on the status of the
     * DB
     * Cache
     * Message Queue
     * Tasks Subsystem
     * Email
    """

    return render(request, "status/status.html", {'db_ok':database_ok(),
                                                  'cache_ok':cache_ok(),
                                                  'data_ok':data_ok()})
