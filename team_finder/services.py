from django.core.paginator import Paginator

from .constants import PAGE_SIZE


def get_page_obj(request, queryset, per_page=PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def get_query_prefix(request, *excluded_params):
    params = request.GET.copy()
    params.pop("page", None)
    for param in excluded_params:
        params.pop(param, None)
    return f"{params.urlencode()}&" if params else ""
