from django.core.cache import caches
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from hospital.models import Role, OperatingRoom, Ward
from .models import MessageLog
from .cache_utils import reset_connection_counts


class CommsModelsTest(TestCase):
    def setUp(self):
        self.nurse_role = Role.objects.get(name='Nurse')
        self.anesthetist_role = Role.objects.get(name='Anesthetist')
        self.surgeon_role = Role.objects.get(name='Surgeon')
        self.or_room = OperatingRoom.objects.first()
        self.ward = Ward.objects.first()

    def test_message_log_creation(self):
        message = MessageLog.objects.create(
            sender_role=self.anesthetist_role,
            recipient_role=self.nurse_role,
            message_type='CAN_ACCEPT_PATIENTS',
            content='Ready to accept new patient',
            location_type='operating_room',
            location_id=self.or_room.id
        )
        self.assertEqual(str(message), f"{self.anesthetist_role} -> {self.nurse_role}: CAN_ACCEPT_PATIENTS")
        self.assertIsNotNone(message.sent_at)
        self.assertIsNone(message.acknowledged_at)

    def test_message_acknowledgment(self):
        message = MessageLog.objects.create(
            sender_role=self.anesthetist_role,
            recipient_role=self.nurse_role,
            message_type='SURGERY_DONE',
            content='Surgery completed',
            location_type='operating_room',
            location_id=self.or_room.id
        )
        message.acknowledged_at = timezone.now()
        message.save()
        self.assertIsNotNone(message.acknowledged_at)


class ConnectionCountResetTests(TestCase):
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
    def test_reset_connection_counts_clears_user_count_entries(self):
        cache_backend = caches['default']
        cache_backend.set('user_count:nurse_ward_1', 5)
        cache_backend.set('user_count:surgeon_ward_2', 3)
        cache_backend.set('unrelated_key', 'value')

        reset_connection_counts()

        self.assertIsNone(cache_backend.get('user_count:nurse_ward_1'))
        self.assertIsNone(cache_backend.get('user_count:surgeon_ward_2'))
        self.assertEqual(cache_backend.get('unrelated_key'), 'value')
