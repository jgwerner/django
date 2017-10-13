# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-10-13 12:50
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import teams.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
        ('billing', '0003_auto_20170807_1114'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=80, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z-]*$', 'You can use only alphanumeric characters.')])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups_created', to=settings.AUTH_USER_MODEL)),
                ('permissions', models.ManyToManyField(blank=True, related_name='team_groups', to='auth.Permission')),
            ],
            options={
                'permissions': (('read_group', 'Read group'), ('write_group', 'Write group')),
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=80, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z-]*$', 'You can use only alphanumeric characters.')])),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('avatar_url', models.CharField(blank=True, max_length=100, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=teams.models.team_directory_path)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('billing_plan', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Plan')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_created', to=settings.AUTH_USER_MODEL)),
                ('default_billing_address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.BillingAddress')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='group',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='teams.Team'),
        ),
    ]
