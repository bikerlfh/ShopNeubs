# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-30 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_apibanner'),
    ]

    operations = [
        migrations.AddField(
            model_name='apibanner',
            name='estado',
            field=models.BooleanField(default=True),
        ),
    ]
