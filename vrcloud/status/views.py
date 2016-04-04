from django.shortcuts import render


def status(request):
    """
    Report on the status of the
     * DB
     * Cache
     * Message Queue
     * Email
     * Tasks Subsystem
    """
    return render("status/status.html", {})
