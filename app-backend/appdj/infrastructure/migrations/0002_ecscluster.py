# Generated by Django 2.2.1 on 2019-05-20 12:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('infrastructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ECSCluster',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clusters', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]