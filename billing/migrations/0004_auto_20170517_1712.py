# -*- coding: utf-8 -*-
# Generated by Django 1.11.2.dev20170517134112 on 2017-05-17 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_delete_billingplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='trial_period_days',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
