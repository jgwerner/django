# -*- coding: utf-8 -*-
# Generated by Django 1.11.6.dev20171101121058 on 2017-11-01 13:21
from __future__ import unicode_literals

from django.db import migrations, models
import appdj.projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectfile',
            name='file',
            field=models.FileField(upload_to=lambda x: x),
        ),
    ]