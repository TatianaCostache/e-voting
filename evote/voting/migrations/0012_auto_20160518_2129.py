# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-18 21:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0011_answer_response'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='question',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='response',
        ),
    ]
