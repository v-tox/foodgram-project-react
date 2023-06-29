from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    """Фильтр ингредиентов."""
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="Ссылка",
    )
    author = filters.ModelChoiceFilter(
        queryset=Recipe.objects.all(),
        field_name="author__id",
        to_field_name="id",
    )
    is_liked = filters.NumberFilter(method='get_is_liked')
    to_buy = filters.NumberFilter(
        method='Избранное'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_liked', 'to_buy')
