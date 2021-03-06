# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-03 11:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_auto_20160503_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='state',
            field=models.CharField(choices=[(b'ACTIVE', b'Activ'), (b'FINISHED', b'Finalizat'), (b'DRAFT', b'Schita')], max_length=15),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(choices=[(b'BUC-S1', b'Bucuresti, Sector 1'), (b'BUC-S2', b'Bucuresti, Sector 2'), (b'BUC-S3', b'Bucuresti, Sector 3'), (b'PITESTI', b'Pitesti'), (b'CONSTANTA', b'Constanta')], max_length=30),
        ),
    ]
