# Generated manually for adding hospital field and updating ward fields

from django.db import migrations, models
import django.db.models.deletion


def create_default_hospital_and_update_locations(apps, schema_editor):
    Hospital = apps.get_model('hospital', 'Hospital')
    OperatingRoom = apps.get_model('hospital', 'OperatingRoom')
    Ward = apps.get_model('hospital', 'Ward')
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

    # Update all existing locations to use the default hospital
    OperatingRoom.objects.update(hospital_id=default_hospital.id)
    Ward.objects.update(hospital_id=default_hospital.id)


def reverse_migration(apps, schema_editor):
    # Nothing to do on reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0007_remove_ward_nurse_telephone_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ward',
            name='telephone',
        ),
        migrations.AddField(
            model_name='ward',
            name='nurse_telephone',
            field=models.CharField(blank=True, help_text='Nurse station telephone number', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='ward',
            name='surgeon_telephone',
            field=models.CharField(blank=True, help_text='Surgeon contact telephone number', max_length=20, null=True),
        ),
        # Add hospital field as nullable first
        migrations.AlterField(
            model_name='operatingroom',
            name='hospital',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='operatingroom_set', to='hospital.hospital'),
        ),
        migrations.AlterField(
            model_name='ward',
            name='hospital',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ward_set', to='hospital.hospital'),
        ),
        # Run data migration
        migrations.RunPython(create_default_hospital_and_update_locations, reverse_migration),
        # Make fields required
        migrations.AlterField(
            model_name='operatingroom',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operatingroom_set', to='hospital.hospital'),
        ),
        migrations.AlterField(
            model_name='ward',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ward_set', to='hospital.hospital'),
        ),
    ]