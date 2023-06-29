import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open('data/ingredients.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for row in data:
            account = Ingredient(
                name=row['name'],
                unit_of_measurement=row['measurement_unit']
            )
            account.save()
