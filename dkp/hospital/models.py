from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Hospital(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name='hospital'
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50)
    website = models.URLField(blank=True, null=True)
    admins = models.ManyToManyField(
        User,
        blank=True,
        related_name='administered_hospitals',
        help_text=_("Users who can administer this hospital (not superusers)")
    )

    def __str__(self):
        return self.short_name or self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True
        unique_together = [['name', 'hospital']]

    def __str__(self):
        return self.name


class OperatingRoom(Location):
    sort = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=_("Sort order for displaying operating rooms")
    )


class Ward(Location):
    sort = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=_("Sort order for displaying wards")
    )
    nurse_telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Nurse station telephone number")
    )
    surgeon_telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Surgeon contact telephone number")
    )


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name