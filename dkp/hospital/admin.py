from django.contrib import admin
from .models import OperatingRoom, Ward, Role


@admin.register(OperatingRoom)
class OperatingRoomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'nurse_telephone', 'surgeon_telephone']
    search_fields = ['name']
    fields = ['name', 'nurse_telephone', 'surgeon_telephone']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']