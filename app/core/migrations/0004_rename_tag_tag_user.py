# Generated by Django 3.2.25 on 2025-01-22 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20250122_0551'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='tag',
            new_name='user',
        ),
    ]