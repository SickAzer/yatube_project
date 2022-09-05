from django.db import models


class CreatedModel(models.Model):
    created = models.DateTimeField(
        'Дата создания',
        db_index=True,
        auto_now_add=True,
        help_text='Дата создания'
    )

    class Meta:
        abstract = True
