# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-09-12 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_log_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='duration',
            field=models.DurationField(blank=True, null=True, verbose_name='Duration'),
        ),
    ]
