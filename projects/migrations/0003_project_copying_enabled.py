# -*- coding: utf-8 -*-
# Generated by Django 1.11.6.dev20171004171408 on 2017-10-04 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_remove_projectfile_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='copying_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
