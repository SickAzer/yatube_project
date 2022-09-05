# Generated by Django 2.2.19 on 2022-09-03 19:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20220903_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, help_text='Дата создания', verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Дата создания', verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Дата создания', verbose_name='Дата создания'),
        ),
    ]