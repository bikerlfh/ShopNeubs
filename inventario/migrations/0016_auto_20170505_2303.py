# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-06 04:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0015_auto_20170417_1428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='saldoinventario',
            options={'permissions': (('consultar_saldo_inventario', 'Puede consultar los saldos de inventario'),), 'verbose_name': 'Saldo Inventario', 'verbose_name_plural': 'Saldo Inventario'},
        ),
    ]
