# Generated by Django 2.2.19 on 2022-09-04 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20220904_1205'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='like',
            name='unique_like',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='liker',
            new_name='user',
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_like'),
        ),
    ]
