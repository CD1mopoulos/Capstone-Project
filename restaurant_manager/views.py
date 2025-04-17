from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from platform_db.models import Dish  # Adjust to your app name
from .forms import DishForm

@login_required
def dish_list(request):
    if not request.user.is_restaurant:
        return HttpResponseForbidden("Access Denied.")

    if not request.user.owned_restaurant:
        return HttpResponseForbidden("No restaurant linked to this user.")

    restaurant = request.user.owned_restaurant
    dishes = Dish.objects.filter(restaurants=restaurant)

    return render(request, 'restaurant_manager/dish_list.html', {
        'restaurant': restaurant,
        'dishes': dishes,
    })
    
    
@login_required
def dish_add(request):
    if not request.user.is_restaurant:
        return HttpResponseForbidden()
    restaurant = request.user.owned_restaurant
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            dish = form.save()
            dish.restaurants.add(restaurant)
            return redirect('dish_list')
    else:
        form = DishForm()
    return render(request, 'restaurant_manager/dish_form.html', {'form': form})

@login_required
def dish_edit(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if not request.user.is_restaurant or request.user.owned_restaurant not in dish.restaurants.all():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            return redirect('dish_list')
    else:
        form = DishForm(instance=dish)
    return render(request, 'restaurant_manager/dish_form.html', {'form': form})

@login_required
def dish_delete(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if not request.user.is_restaurant or request.user.owned_restaurant not in dish.restaurants.all():
        return HttpResponseForbidden()
    dish.delete()
    return redirect('dish_list')
