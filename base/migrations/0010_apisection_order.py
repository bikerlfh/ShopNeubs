# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-08 00:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20170701_0209'),
    ]

    operations = [
        migrations.AddField(
            model_name='apisection',
            name='order',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]