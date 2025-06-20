# Generated by Django 5.1.7 on 2025-05-22 11:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ci_cd', '0002_remove_exercise_resources_remove_exercise_solution_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='resources',
            field=models.TextField(blank=True, help_text='External resources (URLs) for reference', null=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='solution',
            field=models.TextField(default=1, help_text='Detailed solution for instructors (optional)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exercise',
            name='steps',
            field=models.TextField(default='', help_text='Detailed steps to complete this task'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='is_instructor',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_instructor', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
