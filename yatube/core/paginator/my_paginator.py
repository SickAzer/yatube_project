from django.core.paginator import Paginator
from django.conf import settings


def paginate(request, object_list, items_on_page=settings.MAX_POSTS_PER_PAGE):
    paginator = Paginator(object_list, items_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
