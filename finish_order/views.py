from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

def cart_view(request):
    """
    Handles GET and POST requests for the cart.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request.session["cart"] = data.get("cart", [])
            request.session.modified = True  # ✅ Ensures session updates are saved
            return JsonResponse({"message": "Cart updated successfully!"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    cart = request.session.get("cart", [])  # Retrieve cart from session

    orders = []  # Convert session cart to orders list
    for item in cart:
        orders.append({
            "dish_name": item["dishName"],
            "price": item["price"],
            "quantity": item["quantity"]
        })

    return render(request, "finish_order/cart.html", {"orders": orders})


def checkout_view(request):
    """
    Displays the checkout page.
    """
    return render(request, "finish_order/checkout.html")
