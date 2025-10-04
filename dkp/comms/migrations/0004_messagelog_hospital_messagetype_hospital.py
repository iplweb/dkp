# Generated manually for adding hospital field with data migration

from django.db import migrations, models
import django.db.models.deletion
from django.contrib.sites.models import Site


def create_default_hospital_and_set(apps, schema_editor):
    Hospital = apps.get_model('hospital', 'Hospital')
    MessageLog = apps.get_model('comms', 'MessageLog')
    MessageType = apps.get_model('comms', 'MessageType')
    Site = apps.get_model('sites', 'Site')

    # Get or create the default site
    site = Site.objects.first()
    if not site:
        site = Site.objects.create(domain='example.com', name='Example Site')

    # Create a default hospital if none exists
    if not Hospital.objects.exists():
        default_hospital = Hospital.objects.create(
            site=site,
            name='Default Hospital',
            short_name='DH',
            website='https://example.com'
        )
    else:
        default_hospital = Hospital.objects.first()

    # Update all existing MessageLogs to use the default hospital
    MessageLog.objects.update(hospital_id=default_hospital.id)

    # Update all existing MessageTypes to use the default hospital
    MessageType.objects.update(hospital_id=default_hospital.id)


def reverse_migration(apps, schema_editor):
    # Nothing to do on reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('comms', '0003_populate_message_types'),
        ('hospital', '0008_alter_ward_nurse_telephone_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        # First add fields as nullable
        migrations.AddField(
            model_name='messagelog',
            name='hospital',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_logs', to='hospital.hospital'),
        ),
        migrations.AddField(
            model_name='messagetype',
            name='hospital',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_types', to='hospital.hospital'),
        ),
        # Run data migration to set default values
        migrations.RunPython(create_default_hospital_and_set, reverse_migration),
        # Make fields required
        migrations.AlterField(
            model_name='messagelog',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_logs', to='hospital.hospital'),
        ),
        migrations.AlterField(
            model_name='messagetype',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_types', to='hospital.hospital'),
        ),
    ]