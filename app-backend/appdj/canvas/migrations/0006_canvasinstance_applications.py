# Generated by Django 2.1.8 on 2019-03-19 14:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ('canvas', '0005_remove_canvasinstance_applications'),
    ]

    operations = [
        migrations.AddField(
            model_name='canvasinstance',
            name='applications',
            field=models.ManyToManyField(to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ),
    ]