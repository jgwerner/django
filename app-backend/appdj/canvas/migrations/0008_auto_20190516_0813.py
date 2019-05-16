# Generated by Django 2.2.1 on 2019-05-16 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0007_canvasinstance_admins'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='canvasinstance',
            options={'permissions': (('is_admin', 'Is admin'),)},
        ),
        migrations.RenameField(
            model_name='canvasinstance',
            old_name='admins',
            new_name='users',
        ),
    ]
