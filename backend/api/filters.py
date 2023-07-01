from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
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
        to_field_name="slug",
    )
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(is_liked__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(to_buy__user=self.request.user)
        return queryset