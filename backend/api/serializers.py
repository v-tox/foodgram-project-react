import re

from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import (BuyList, Ingredient, IngredientSum,
                            Liked, Recipe, Tag)
from users.models import User, Follow

from .fields import Base64ImageField
from rest_framework import serializers


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')


    def validate_username(self, value):
        pattern = re.compile('^[\\w]{3,}')
        if re.match(pattern=pattern, string=value) is None:
            raise serializers.ValidationError('Недопустимые символы.')
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать имя пользователя me.'
            )
        return value


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.following.filter(user=user).exists()
        return False

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


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Your old password was entered incorrectly'
            )
        return value

    def validate_new_password(self, value):
        validate_password(value)
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
    measurement_unit = serializers.CharField(
        source='ingredient.unit_of_measurement',
        read_only=True
    )
    amount = serializers.IntegerField(source='sum')

    class Meta:
        model = IngredientSum
        fields = ('id', 'amount', 'name', 'measurement_unit')


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
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(
        required=False,
        allow_null=True
    )
    cooking_time = serializers.IntegerField(source='cook_time')
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.id in self.context['liked']
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.id in self.context['to_buy']
        return False

    def validate_recipe(self, value):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        if Liked.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже'
                                              'добавлен в понравившиеся')
        if BuyList.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Уже в списке')
        return value


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = IngredientSumSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all().only(
                                                  'id'))

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe_id=recipe.id, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        super().update(instance, validated_data)
        if tags:
            instance.tags.set(tags)

        if ingredients:
            IngredientSum.objects.filter(recipe=instance).delete()
            self.create_ingredients(
                recipe_id=instance.id,
                ingredients=ingredients
            )
        return instance

    def create_ingredients(self, recipe_id, ingredients):
        new_ingredients = []
        for ingredient in ingredients:
            new_ingredients.append(
                IngredientSum(
                    recipe_id=recipe_id,
                    ingredient_id=ingredient['ingredient']['id'].id,
                    sum=ingredient['sum']
                )
            )
        IngredientSum.objects.bulk_create(new_ingredients)

    def validate_ingredients(self, ingredients):
        ingredient_ids = []
        validate_ingredients = []
        for ingredient in ingredients:
            if ingredient['ingredient']['id'].id in ingredient_ids:
                continue
            ingredient_ids.append(ingredient['ingredient']['id'].id)
            validate_ingredients.append(ingredient)

            if not (0 < ingredient['sum'] < 10000):
                raise serializers.ValidationError(
                    'Недопустимое значение количествава ингредиентов.'
                )
        return validate_ingredients

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
        author = get_object_or_404(User, id=id)
        if user.id == author.id:
            raise serializers.ValidationError('Вы не можете подписаться'
                                              'на самого себя')
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Вы уже подписаны')
        return value
