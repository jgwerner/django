# Generated by Django 2.2.1 on 2019-07-13 07:48

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0001_initial'),
        ('projects', '0019_auto_20190325_1435'),
        ('canvas', '0010_auto_20190521_0921'),
        ('assignments', '0002_auto_20190618_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='path',
            field=models.FilePathField(max_length=255, path='/tmp/tmpxa72bzdq'),
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('external_id', models.TextField()),
                ('path', models.FilePathField(max_length=255, path='/tmp/tmpxa72bzdq')),
                ('course_id', models.TextField()),
                ('source_did', models.TextField()),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lms_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='canvas.CanvasInstance')),
                ('oauth_app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modules', to='oauth2.Application')),
                ('students_projects', models.ManyToManyField(related_name='student_modules', to='projects.Project')),
                ('teacher_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_modules', to='projects.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]