from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class OperatingRoom(Location):
    pass


class Ward(Location):
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Ward contact telephone number")
    )


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name