from django.contrib import admin
from .models import MessageLog, MessageType


@admin.register(MessageType)
class MessageTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'source_role', 'target_role', 'short_description_en', 'display_order', 'is_active']
    list_filter = ['source_role', 'target_role', 'is_active']
    search_fields = ['code', 'short_description_en', 'short_description_pl']
    ordering = ['display_order', 'code']

    # Make code field readonly in admin
    readonly_fields = ['code']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'source_role', 'target_role')
        }),
        ('English Translations', {
            'fields': ('short_description_en', 'full_description_en')
        }),
        ('Polish Translations', {
            'fields': ('short_description_pl', 'full_description_pl')
        }),
        ('Display Settings', {
            'fields': ('button_color', 'display_order', 'is_active')
        })
    )


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['sender_role', 'recipient_role', 'message_type', 'location_info', 'sent_at', 'acknowledged_at']
    list_filter = ['sender_role', 'recipient_role', 'message_type', 'location_type']
    search_fields = ['content']
    readonly_fields = ['sent_at', 'acknowledged_at']

    def location_info(self, obj):
        if obj.location_type == 'operating_room':
            from hospital.models import OperatingRoom
            try:
                location = OperatingRoom.objects.get(id=obj.location_id)
                return f"OR: {location.name}"
            except OperatingRoom.DoesNotExist:
                return f"OR (ID: {obj.location_id})"
        else:
            from hospital.models import Ward
            try:
                location = Ward.objects.get(id=obj.location_id)
                return f"Ward: {location.name}"
            except Ward.DoesNotExist:
                return f"Ward (ID: {obj.location_id})"
    location_info.short_description = 'Location'