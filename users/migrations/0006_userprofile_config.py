# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-02 15:21
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20180109_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]