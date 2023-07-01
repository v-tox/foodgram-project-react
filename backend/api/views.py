# я исправила уже всё, что только можно было.
# нашла причину ошибки, нашла поломанный сериализатор рецептов
# и еще кучу всего. школьники с ютуба круче меня(
from django.db.models import Sum
from django.http import HttpResponse
from django.db.models import Prefetch, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )
from recipes.models import (BuyList, Ingredient, IngredientSum,
                            Liked, Recipe, Tag)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .paginator import LimitPageNumberPagination
from .serializers import (UserSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializer,
                          FollowSerializer,
                          UserCreateSerializer,
                          ChangePasswordSerializer,
                          RecipeCreateSerializer
                          )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial']:
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def me(self, *args, **kwargs):
        user = get_object_or_404(User, id=self.request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def set_password(self, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=self.request.data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(
            data={
                'status': f'Set new password '
                          f'user {self.request.user.username}'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, *args, **kwargs):
        recipes_limit = int(self.request.GET.get('recipes_limit'))
        subquery = Subquery(
            Recipe.objects.order_by('-pub_date')
            .values_list('id', flat=True)[:recipes_limit + 1]
        )
        queryset = User.objects.filter(
            following__user=self.request.user
        ).prefetch_related(
            Prefetch('recipes',
                     queryset=Recipe.objects.filter(id__in=subquery))
        )[:recipes_limit]
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      context={'request': self.request},
                                      many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if self.request.method == 'POST':
            Follow.objects.create(author=author, user=self.request.user)
            serializer = UserSerializer(author,
                                        context={'request': self.request})
            return Response(serializer.data, status.HTTP_201_CREATED)

        Follow.objects.filter(author=author,
                              user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'is_favorited': set(),
            'is_in_shopping_cart': set()
        }
        user = self.request.user
        if user.is_authenticated:
            context['liked'] = set(Liked.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True))
            context['to_buy'] = set(BuyList.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True))
        return context

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if self.request.method == 'POST':
            Liked.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            is_liked = get_object_or_404(Liked, user=user, recipe=recipe)
            is_liked.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if self.request.method == 'POST':
            BuyList.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                BuyList, user=user, recipe=recipe)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientSum.objects
            .filter(recipe__to_buy__user=request.user)
            .select_related('recipe')
            .annotate(total_sum=Sum('sum'))
            .values_list('ingredient__name', 'total_sum',
                         'ingredient__unit_of_measurement')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient[0]} - '
                f'{ingredient[1]} '
                f'{ingredient[2]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'buy_list.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
