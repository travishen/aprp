# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-09-12 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Url'),
        ),
    ]
