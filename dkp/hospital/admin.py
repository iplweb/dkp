from django.contrib import admin
from .models import Hospital, OperatingRoom, Ward, Role


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'name', 'website', 'site']
    search_fields = ['name', 'short_name']
    fields = ['site', 'name', 'short_name', 'website']


@admin.register(OperatingRoom)
class OperatingRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital']
    search_fields = ['name']
    list_filter = ['hospital']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'nurse_telephone', 'surgeon_telephone']
    search_fields = ['name']
    list_filter = ['hospital']
    fields = ['name', 'hospital', 'nurse_telephone', 'surgeon_telephone']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']