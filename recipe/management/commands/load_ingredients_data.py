import csv

from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'load Ingredients Data to database'

    def handle(self, *args, **kwargs):
        with open('recipe/fixtures/ingredients.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(name=name, unit=unit)
