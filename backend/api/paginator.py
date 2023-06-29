from rest_framework.pagination import PageNumberPagination

RECIPES_PER_PAGE: int = 6


class LimitPageNumberPagination(PageNumberPagination):
    page_size = RECIPES_PER_PAGE
    page_size_query_param = 'limit'
