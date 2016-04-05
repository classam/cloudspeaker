from django.utils import timezone
from django.db import models


class DatabaseStatus(models.Model):
    """
    A dummy model. Write to the database to make sure that we can.
    Then, read from the database to make sure that we can.
    """
    created = models.DateTimeField()

    def save(self):
        if not self.id:
            self.created = timezone.now()

    @classmethod
    def write_ok(cls) -> bool:
        s = cls()
        s.save()
        return True

    @classmethod
    def read_ok(cls) -> bool:
        cls.objects.all().order_by('-created')[0]
        return True
