# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-17 02:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20170817_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=9.99, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=6.99, max_digits=100, null=True),
        ),
    ]
