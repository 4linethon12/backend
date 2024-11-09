# Generated by Django 5.1.3 on 2024-11-08 18:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groups', '0002_recommendedmission_group_group_leader_group_mission_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ManitoMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('giver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='giver', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.group')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ManitoMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hint', models.TextField()),
                ('letter', models.TextField()),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manito.manitomatch')),
            ],
        ),
    ]
