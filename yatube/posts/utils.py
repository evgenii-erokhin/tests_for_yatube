from django.conf import settings
from django.core.paginator import Paginator


def get_pages(request, post_list):
    paginator = Paginator(post_list, settings.NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
