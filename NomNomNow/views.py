from django.shortcuts import render
from platform_db.models import Restaurant, Dish

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def restaurant_list(request):
    restaurants = Restaurant.objects.all()  # Retrieve all restaurant records
    return render(request, 'index.html', {'restaurants': restaurants})

def menu_list(request):
    dishes = Dish.objects.all()
    return render(request, 'platform_db/menus.html', {'dishes': dishes})