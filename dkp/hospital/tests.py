from django.test import TestCase
from .models import OperatingRoom, Ward, Role


class HospitalModelsTest(TestCase):
    def test_operating_room_creation(self):
        room = OperatingRoom.objects.create(name="Test OR")
        self.assertEqual(str(room), "Test OR")
        self.assertEqual(room.name, "Test OR")

    def test_ward_creation(self):
        ward = Ward.objects.create(name="Test Ward")
        self.assertEqual(str(ward), "Test Ward")
        self.assertEqual(ward.name, "Test Ward")

    def test_role_creation(self):
        role = Role.objects.create(name="Test Role")
        self.assertEqual(str(role), "Test Role")
        self.assertEqual(role.name, "Test Role")