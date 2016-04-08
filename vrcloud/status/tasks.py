from __future__ import absolute_import

from celery import shared_task

from .models import CeleryStatus


@shared_task
def tick():
    c = CeleryStatus()
    c.save()
    print("Celery's working!")
