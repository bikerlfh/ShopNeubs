# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-08 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_apisection_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apisection',
            old_name='order',
            new_name='orden',
        ),
    ]
