# -*- coding: utf-8 -*-
# Generated by Django 1.11.4.dev20170804115648 on 2017-08-07 11:14
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0002_auto_20170803_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='serversize',
            name='cost_per_second',
            field=models.DecimalField(decimal_places=6, default=Decimal('0.000000'), help_text='Price in USD ($) per second it costs to run a server of this size.', max_digits=7),
        ),
    ]