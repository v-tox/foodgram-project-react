from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


MAX_INGREDIENT_LENGTH: int = 150
MAX_UNIT_OF_MEASURE_LENGTH: int = 150
MAX_TAG_NAME_LENGTH: int = 50
MAX_TAG_COLOR_LENGTH: int = 7
MAX_RECIPE_NAME_LENGTH: int = 50


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=MAX_INGREDIENT_LENGTH,
        verbose_name='Ингредиент',
    )
    unit_of_measurement = models.CharField(
        max_length=MAX_UNIT_OF_MEASURE_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.unit_of_measurement}'


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=MAX_TAG_NAME_LENGTH,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=MAX_TAG_COLOR_LENGTH,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный URL',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LENGTH,
        verbose_name='Название',
    )
    image = models.ImageField(
        blank=True,
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        related_name='recipes')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(
            1,
            message='Время приготовления не может быть'
                    'меньше одной минуты =(')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientSum(models.Model):
    """Модель подсчета количества ингредиентов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    sum = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='В рецепте не может быть'
                                                 'меньше одного ингредиента')]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]

    def __str__(self):
        return f'{self.ingredient}: {self.sum}'


class Liked(models.Model):
    """Модель избранного."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_liked',
        verbose_name='Понравившийся рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='like',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class BuyList(models.Model):
    """Модель списка покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='to_buy',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buy_list',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в Список покупок'
