import datetime

from posts.models import Group


def groups_all(request):
    """Добавляет переменную с текущим годом."""
    return {
        'groups_all': Group.objects.all()
    }

