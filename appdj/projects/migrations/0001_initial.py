# -*- coding: utf-8 -*-
# Generated by Django 1.11.4.dev20170714110119 on 2017-07-14 15:07
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import appdj.projects.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('social_django', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaborator',
            fields=[
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('owner', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('name', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z-]*$', 'You can use only alphanumeric characters.')])),
                ('description', models.CharField(blank=True, max_length=400)),
                ('private', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('collaborators', models.ManyToManyField(related_name='projects', through='projects.Collaborator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('write_project', 'Write project'), ('read_project', 'Read project')),
            },
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('file', models.FileField(upload_to=lambda x: x)),
                ('public', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='projects.Project')),
            ],
        ),
        migrations.CreateModel(
            name='SyncedResource',
            fields=[
                ('folder', models.CharField(max_length=50)),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_django.UserSocialAuth')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synced_resources', to='projects.Project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='integrations',
            field=models.ManyToManyField(related_name='projects', through='projects.SyncedResource', to='social_django.UserSocialAuth'),
        ),
        migrations.AddField(
            model_name='collaborator',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project'),
        ),
        migrations.AddField(
            model_name='collaborator',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
