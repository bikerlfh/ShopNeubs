# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-06 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carousel',
            name='url',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
    ]