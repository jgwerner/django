# -*- coding: utf-8 -*-
# Generated by Django 1.11.2.dev20170519134547 on 2017-05-22 16:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0008_auto_20170522_1628'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='dynamic_last_four',
            new_name='dynamic_last4',
        ),
        migrations.RenameField(
            model_name='card',
            old_name='last_four',
            new_name='last4',
        ),
    ]