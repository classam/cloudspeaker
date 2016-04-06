from django.shortcuts import render
from .models import DatabaseStatus


def status(request):
    """
    Diagnostics!

    Report on the status of the
     * DB
     * Cache
     * Message Queue
     * Email
     * Tasks Subsystem
    """

    db_ok = DatabaseStatus.ok()

    return render(request, "status/status.html", {'db_ok':db_ok})
