# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-17 02:24
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20170816_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thumbnail',
            name='user',
        ),
        migrations.AlterField(
            model_name='product',
            name='media',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\ASUS\\Documents\\python_work\\Web Application\\dm\\static_cdn\\protected'), upload_to=products.models.download_media_location),
        ),
    ]
