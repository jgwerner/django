# Generated by Django 2.1.8 on 2019-03-25 14:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_auto_20190315_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='project',
            name='integrations',
            field=models.ManyToManyField(blank=True, related_name='projects', to='social_django.UserSocialAuth'),
        ),
    ]