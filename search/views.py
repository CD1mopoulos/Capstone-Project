from django.shortcuts import render
from django.db.models import Q
from platform_db.models import Restaurant, Dish

def search_results(request):
    query = request.GET.get('q', '')
    matched_restaurants = []
    matched_dishes = []

    if query:
        matched_restaurants = Restaurant.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(address__icontains=query)
        ).distinct()

        matched_dishes = Dish.objects.filter(
            Q(dish_name__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(description__icontains=query) |
            Q(search_tag__icontains=query)
        ).distinct()

    return render(request, 'search/search_results.html', {
        'query': query,
        'matched_restaurants': matched_restaurants,
        'matched_dishes': matched_dishes,
    })
