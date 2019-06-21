# Generated by Django 2.2.1 on 2019-06-19 11:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0019_auto_20190325_1435'),
        ('canvas', '0010_auto_20190521_0921'),
        ('oauth2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('external_id', models.TextField()),
                ('path', models.FilePathField(path='/workspaces')),
                ('course_id', models.TextField()),
                ('outcome_url', models.URLField()),
                ('source_did', models.TextField()),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lms_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='canvas.CanvasInstance')),
                ('oauth_app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments', to='oauth2.Application')),
                ('students_projects', models.ManyToManyField(related_name='student_assignments', to='projects.Project')),
                ('teacher_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='projects.Project')),
            ],
        ),
    ]