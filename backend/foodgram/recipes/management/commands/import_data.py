import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

            for row in data:
                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],)
                ingredient.save()
