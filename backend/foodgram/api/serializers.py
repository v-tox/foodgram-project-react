import re
from django.shortcuts import get_object_or_404
from recipes.models import (Ingredient, IngredientSum,
                            Recipe, Tag)
from users.models import User, Follow
from recipes.models import BuyList, Liked
from .fields import Base64ImageField
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'is_subscribed',
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(), fields=['email', 'username']
            )
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def validate_username(self, value):
        pattern = re.compile('^[\\w]{3,}')
        if re.match(pattern=pattern, string=value) is None:
            raise serializers.ValidationError('Недопустимые символы.')
        return value

    def validate(self, data):
        email = data.get('email', None)
        if User.objects.filter(email=email).exists():
            if data['username'] != User.objects.get(email=email).username:
                raise serializers.ValidationError(
                    'Этот email занят.'
                )

        return super().validate(data)


class NewUserSerializer(serializers.ModelSerializer):
    """Сериализатор нового пользователя."""
    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate_username(self, value):
        pattern = re.compile('^[\\w]{3,}')
        if re.match(pattern=pattern, string=value) is None:
            raise serializers.ValidationError('Недопустимые символы.')
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать имя пользователя me.'
            )
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSumSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    unit_of_measurement = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientSum
        fields = ('id', 'sum', 'name', 'unit_of_measurement')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = IngredientSumSerializer(
        many=True, source='recipe_ingredients',
    )
    author = UserSerializer(
        read_only=True,
    )
    is_liked = serializers.SerializerMethodField(read_only=True)
    to_buy = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_liked',
            'to_buy', 'name', 'image', 'text', 'cook_time'
        )

# опять же, надеюсь, что правильно поняла.
# сейчас даже на вопрос 'как меня зовут' не уверена,
# что правильно отвечу
    def get_is_liked(self, obj):
        return (self.context.get('request').user.is_authenticated
                and obj.id in self.context['liked'])

    def get_to_buy(self, obj):
        return (self.context.get('request').user.is_authenticated
                and obj.id in self.context['to_buy'])

    def validate_recipe(self, value):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=id)
        if Liked.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже'
                                              'добавлен в понравившиеся')
        if BuyList.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Уже в списке')
        return value


class FollowSerializer(UserSerializer):
    '''Сериализатор подписoк.'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return RecipeSerializer(
            recipes, many=True, context=self.context).data

    def validate_follow(self, value):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if user.id == author.id:
            raise serializers.ValidationError('Вы не можете подписаться'
                                              'на самого себя')
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Вы уже подписаны')
        return value
