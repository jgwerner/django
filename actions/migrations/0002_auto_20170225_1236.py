# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 12:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ('-start_date',)},
        ),
    ]
