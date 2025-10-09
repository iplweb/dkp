from django.contrib import admin
from .models import Hospital, OperatingRoom, Ward, Role


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'name', 'website', 'site', 'admin_count']
    search_fields = ['name', 'short_name']
    fields = ['site', 'name', 'short_name', 'website', 'admins']
    filter_horizontal = ['admins']  # Nice widget for ManyToMany

    def admin_count(self, obj):
        """Display count of hospital admins"""
        count = obj.admins.count()
        return f"{count} admin(s)"
    admin_count.short_description = 'Hospital Admins'


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