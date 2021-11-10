from django.forms import ModelForm, TextInput

from .models import Stream


# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ['name', 'description', 'cook_time', 'image']


# class IngredientForRecipeForm(ModelForm):
#     class Meta:
#         model = IngredientForRecipe
#         fields = ['ingredient', 'quantity']
#         widgets = {'ingredient': TextInput}


class StreamForm(ModelForm):
    class Meta:
        model = Stream
        fields = ['key', 'image', 'title']