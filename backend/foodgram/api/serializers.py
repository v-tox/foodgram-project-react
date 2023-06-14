import re
from django.contrib.auth import get_user_model
import base64
from recipes.models import (Ingredient, IngredientSum,
                            Recipe, Tag)
from django.core.files.base import ContentFile
from rest_framework import serializers

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

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


class FollowSerializer(UserSerializer):
    '''Сериализатор подписoк.'''
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
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
    is_liked = serializers.BooleanField(read_only=True)
    to_buy = serializers.BooleanField(read_only=True)
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

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(liked__user=user, id=obj.id).exists()

    def get_to_buy(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.buylist.filter(recipe=obj.id).exists()
