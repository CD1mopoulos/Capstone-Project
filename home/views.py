from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from platform_db.models import Restaurant, Dish, OrderItem, PurchasedDish
from collections import Counter

def index(request):
    restaurants = Restaurant.objects.all()
    dishes = Dish.objects.all()
    
    # Fetch the cart items for the logged-in user
    orders = OrderItem.objects.filter(user=request.user) if request.user.is_authenticated else None

    return render(request, 'home/index.html', {
        'restaurants': restaurants,
        'dishes': dishes,
        'orders': orders  # Pass orders to the template
    })

def terms_conditions(request):
    return render(request, 'home/terms_conditions.html')

def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')

# ✅ Place this function below the existing views
def cart_view(request):
    """
    Displays the cart page with the user's items.
    - POST: Updates the cart in Django session (from JavaScript).
    - GET: Loads the cart page with session data.
    """
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request.session["cart"] = data.get("cart", [])  # ✅ Save cart to session
            request.session.modified = True
            return JsonResponse({"message": "Cart updated successfully!"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # ✅ Retrieve cart from session when loading /cart/
    cart = request.session.get("cart", [])

    return render(request, "finish_order/cart.html", {"orders": cart})

def rec_dish(request):
    print("🔁 rec_dish() view is being called!")
    user = request.user
    recommended_dishes = []
    used_fallback = False

    if user.is_authenticated:
        # 🧠 PERSONALIZED RECOMMENDATIONS FOR LOGGED-IN USERS

        # Get all previously purchased dishes by this user
        purchased_dishes = PurchasedDish.objects.filter(purchase__user=user)

        if purchased_dishes.exists():
            dish_counter = Counter()
            for pd in purchased_dishes:
                dish_counter[pd.dish_id] += pd.quantity

            # Get top 6 most frequently ordered dish IDs by this user
            top_dish_ids = [dish_id for dish_id, _ in dish_counter.most_common(6)]

            # Preserve the order of dish IDs
            dish_map = {
                dish.dish_id: dish
                for dish in Dish.objects.filter(dish_id__in=top_dish_ids)
            }
            recommended_dishes = [dish_map[d_id] for d_id in top_dish_ids if d_id in dish_map]
        else:
            used_fallback = True

    if not recommended_dishes:
        used_fallback = True
        # 🌍 GLOBAL FALLBACK RECOMMENDATIONS (FOR LOGGED-OUT USERS OR EMPTY HISTORY)

        global_counter = Counter()
        for pd in PurchasedDish.objects.all():
            global_counter[pd.dish_id] += pd.quantity

        # Get top 6 most purchased dishes globally
        top_global_ids = [dish_id for dish_id, _ in global_counter.most_common(6)]
        dish_map = {
            dish.dish_id: dish
            for dish in Dish.objects.filter(dish_id__in=top_global_ids)
        }
        recommended_dishes = [dish_map[d_id] for d_id in top_global_ids if d_id in dish_map]

    restaurants = Restaurant.objects.all()

    print("✅ USER:", user.username if user.is_authenticated else "Anonymous")
    print("✅ Used fallback?", used_fallback)
    print("✅ Recommended Dishes:", [d.dish_name for d in recommended_dishes])
    print("✅ Total dishes being passed:", len(recommended_dishes))

    context = {
        'dishes': recommended_dishes,
        'used_fallback': used_fallback,
        'restaurants': restaurants,
    }
    return render(request, 'home/index.html', context)
