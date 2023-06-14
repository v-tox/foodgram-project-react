from django.contrib import admin

from .models import (Liked, Ingredient, IngredientSum, Recipe,
                     BuyList, Tag)


'''Модели для админки.'''


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_of_measurement')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'id', 'name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    @staticmethod
    def get_liked(obj):
        return obj.liked.count()


@admin.register(Liked)
class LikedAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')


@admin.register(BuyList)
class BuyListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    empty_value_display = '-пусто-'


@admin.register(IngredientSum)
class IngredientSumAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'sum')
    empty_value_display = '-пусто-'
