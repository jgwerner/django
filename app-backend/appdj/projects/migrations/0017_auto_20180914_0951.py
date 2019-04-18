# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-09-14 09:51
from __future__ import unicode_literals

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_project_config'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='project',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name', 'description'], name='projects_pr_name_4daf64_gin'),
        ),
    ]