from django.core.paginator import Paginator


def paginate(request, object_list, posts_per_page=10):
    paginator = Paginator(object_list, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
