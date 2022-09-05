# Generated by Django 2.2.19 on 2022-09-04 18:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_auto_20220904_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, default=None, help_text='Пользователи, лайкнувшие пост', related_name='like', to=settings.AUTH_USER_MODEL),
        ),
    ]
