# Generated by Django 2.2.19 on 2022-09-03 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_auto_20220903_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, help_text='Дайте описание группы', null=True, verbose_name='Описание группы'),
        ),
    ]
