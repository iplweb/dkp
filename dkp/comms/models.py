from django.db import models
from django.utils.translation import gettext_lazy as _
from hospital.models import Hospital, Role, OperatingRoom, Ward


class MessageType(models.Model):
    """
    Defines the types of messages that can be sent in the system.
    Each message type has a source role, target role, and translations.
    """
    ROLE_CHOICES = [
        ('Anesthetist', _('Anesthetist')),
        ('Nurse', _('Nurse')),
        ('Surgeon', _('Surgeon')),
    ]

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='message_types'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Internal message code (readonly in admin)")
    )
    source_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text=_("Role that can send this message")
    )
    target_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text=_("Role that will receive this message")
    )

    # English translations
    short_description_en = models.CharField(
        max_length=100,
        help_text=_("Short English description shown on buttons")
    )
    full_description_en = models.TextField(
        help_text=_("Full English description explaining the message")
    )

    # Polish translations
    short_description_pl = models.CharField(
        max_length=100,
        help_text=_("Short Polish description shown on buttons")
    )
    full_description_pl = models.TextField(
        help_text=_("Full Polish description explaining the message")
    )

    # UI settings
    button_color = models.CharField(
        max_length=20,
        default='danger',
        help_text=_("Bootstrap button color class (danger, warning, success, etc.)")
    )
    display_order = models.IntegerField(
        default=0,
        help_text=_("Order in which buttons are displayed (lower numbers first)")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this message type is currently available")
    )

    class Meta:
        ordering = ['display_order', 'code']
        verbose_name = _("Message Type")
        verbose_name_plural = _("Message Types")

    def __str__(self):
        return f"{self.code} ({self.source_role} → {self.target_role})"

    def get_short_description(self, language_code='en'):
        """Get short description based on language."""
        if language_code == 'pl':
            return self.short_description_pl
        return self.short_description_en

    def get_full_description(self, language_code='en'):
        """Get full description based on language."""
        if language_code == 'pl':
            return self.full_description_pl
        return self.full_description_en


class MessageLog(models.Model):
    MESSAGE_TYPES = [
        ('CAN_ACCEPT_PATIENTS', _('Can Accept Patients')),
        ('SURGERY_DONE', _('Surgery Done')),
        ('PATIENT_IN_THE_OR', _('Patient in the OR')),
    ]

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='message_logs'
    )
    sender_role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='sent_messages')
    recipient_role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    content = models.TextField()

    # Explicit foreign keys for both locations
    operating_room = models.ForeignKey(
        OperatingRoom,
        on_delete=models.CASCADE,
        related_name='message_logs',
        default=11  # Default to first operating room
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='message_logs',
        default=15  # Default to first ward
    )

    sent_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    no_users_who_received = models.IntegerField(
        default=0,
        help_text=_("Number of users who were connected to receive this message when it was sent")
    )

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.sender_role} -> {self.recipient_role}: {self.message_type}"