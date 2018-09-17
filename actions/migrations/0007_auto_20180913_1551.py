# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-09-13 15:51
from __future__ import unicode_literals

import actions.utils
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0006_action_headers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='headers',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}, encoder=actions.utils.SkipJSONEncoder),
        ),
    ]