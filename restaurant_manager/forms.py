from django import forms
from platform_db.models import Dish  # Import Dish from correct app

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['dish_name', 'price', 'description', 'ingredients', 'search_tag', 'photo']
