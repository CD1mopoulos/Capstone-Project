from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction
from django.db.models import F, Count, Sum
from allauth.socialaccount.models import SocialAccount
from platform_db.forms import CustomUserSignupForm
from .models import (
    CartItem, UserDetails, Restaurant, Dish,
    CustomUser, OrderItem, Purchase, PurchasedDish, DeliveryOrder
)
import json, time, requests, traceback, logging
from django.apps import AppConfig
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


logger = logging.getLogger(__name__)

def restaurant_list(request):
    restaurants = Restaurant.objects.all()  # Fetch restaurants from the database
    return render(request, 'restaurants.html', {'restaurants': restaurants})

@csrf_exempt  # Temporarily allow CSRF (use CSRF token properly in production)
def signup(request):
    if request.method == "POST":
        # Check if user is signing up via social login (Facebook)
        if request.user.is_authenticated and SocialAccount.objects.filter(user=request.user).exists():
            return JsonResponse({"success": True, "message": "Signed up with Facebook successfully!"})

        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set the authentication backend explicitly
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, user)  # Log the user in
            return JsonResponse({"success": True})  # Success response

        else:
            return JsonResponse({"success": False, "error": form.errors.as_json()})  # Return errors

    return JsonResponse({"success": False, "error": "Invalid request method."})


def complete_signup(request):
    """Check if the user has missing fields, redirect them to complete their profile."""
    social_account = SocialAccount.objects.filter(user_id=request.user.user_id).first()

    
    if not social_account:
        return redirect("/")  # Not a social account, go to home
    
    # Redirect user to complete profile if they are missing fields
    if not request.user.first_name or not request.user.email:
        return redirect("/update-profile/")  # Redirect to profile completion page

    return redirect("/")  # If everything is fine, go to home

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            # AJAX login
            if request.content_type == 'application/json':
                if not request.body:
                    return JsonResponse({'success': False, 'error': 'Empty request body'}, status=400)
                data = json.loads(request.body.decode('utf-8'))

            # Normal Form POST login
            else:
                data = {
                    'username': request.POST.get('username', '').strip(),
                    'password': request.POST.get('password', '').strip(),
                    'remember_me': request.POST.get('remember_me', False),
                }

            username = data.get('username', '')
            password = data.get('password', '')
            remember_me = data.get('remember_me', False)

            if not username or not password:
                error_response = {'success': False, 'error': 'Username and password are required'}
                return JsonResponse(error_response, status=400) if request.content_type == 'application/json' else render(request, 'platform_db/login.html', {'error': error_response['error']})

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session.set_expiry(1209600 if remember_me else 0)

                # Ajax Response
                if request.content_type == 'application/json':
                    return JsonResponse({'success': True, 'redirect_url': reverse('home')})
                
                # Form Response → Redirect
                return redirect('home')

            error_response = {'success': False, 'error': 'Invalid credentials'}
            return JsonResponse(error_response, status=401) if request.content_type == 'application/json' else render(request, 'platform_db/login.html', {'error': error_response['error']})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    # GET → Show Login Page
    return render(request, 'platform_db/login.html')

@login_required
def update_profile(request):
    user_details, created = UserDetails.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_details.address = request.POST.get("address", user_details.address)
        user_details.phone = request.POST.get("phone", user_details.phone)
        user_details.payment_method = request.POST.get("payment_method", user_details.payment_method)
        user_details.allergies = request.POST.get("allergies", user_details.allergies)
        user_details.save()

        # Redirect back to the home page after saving
        return redirect('home')

    # Redirect if method is not POST
    return redirect('home')


def custom_logout(request):
    logout(request)
    return redirect('/')

def restaurant_menu(request, rest_id):
    restaurant = get_object_or_404(Restaurant, pk=rest_id)
    dishes = Dish.objects.filter(restaurants=restaurant)  # Corrected Many-to-Many Query

    context = {
        'restaurant': restaurant,
        'dishes': dishes,
        'show_menu': True  # A flag to control menu visibility in index.html
    }
    return render(request, 'home/index.html', context)


def get_menu(request, rest_id):
    restaurant = get_object_or_404(Restaurant, rest_id=rest_id)
    dishes = Dish.objects.filter(restaurants=restaurant).values(  # ✅ Fetch values directly
        "dish_id", "dish_name", "price", "description", "ingredients", "photo"
    )

    # Convert query results to a list
    menu_data = list(dishes)

    # Convert photo URL if available
    for dish in menu_data:
        if dish["photo"]:  
            dish["photo"] = request.build_absolute_uri(settings.MEDIA_URL + dish["photo"])

    return JsonResponse({"menu_items": menu_data})



def get_nearby_restaurants(request):
    try:
        dish_id = request.GET.get('dish_id')
        user_lat = request.GET.get('lat')
        user_lon = request.GET.get('lon')

        # Validate input
        if not dish_id or not user_lat or not user_lon:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # Convert lat/lon to float
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            dish_id = int(dish_id)  # Ensure dish_id is an integer
        except ValueError:
            return JsonResponse({"error": "Invalid latitude, longitude, or dish_id values"}, status=400)

        # Get the dish and associated restaurants
        dish = Dish.objects.prefetch_related("restaurants").filter(dish_id=dish_id).first()

        if not dish:
            return JsonResponse({"error": "Dish not found."}, status=404)

        restaurants = dish.restaurants.all()  # Get all linked restaurants

        if not restaurants:
            return JsonResponse({"error": "No restaurants found serving this dish."}, status=404)

        # Compute distances using latitude and longitude fields
        results = []
        for rest in restaurants:
            if rest.latitude is None or rest.longitude is None:
                print(f"⚠️ Skipping restaurant {rest.name} due to missing latitude/longitude")
                continue  # Skip restaurants with missing coordinates

            distance = round(((rest.latitude - user_lat) ** 2 + 
                              (rest.longitude - user_lon) ** 2) ** 0.5, 2)
            results.append({"rest_id": rest.rest_id, "name": rest.name, "distance": distance})

        # Sort restaurants by distance
        results = sorted(results, key=lambda x: x["distance"])

        return JsonResponse({"restaurants": results})

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ ERROR in get_nearby_restaurants:\n{error_details}")  # Print full traceback
        return JsonResponse({"error": str(e)}, status=500)

    
def facebook_login(request):
    user = request.user
    if user.is_authenticated:
        try:
            fb_account = SocialAccount.objects.get(user=user, provider="facebook")
            return redirect("home")  # Redirect to dashboard or home page
        except SocialAccount.DoesNotExist:
            return redirect("/accounts/facebook/login/")
    return redirect("/accounts/facebook/login/")


def facebook_signup(request):
    if request.user.is_authenticated:
        try:
            social_account = SocialAccount.objects.get(user=request.user, provider="facebook")

            # Ensure user has a valid email & username before redirecting
            if not request.user.email or not request.user.username:
                return redirect("/platform_db/complete-signup/")  # Redirect user to complete profile
            
            return redirect("home")

        except SocialAccount.DoesNotExist:
            return redirect("/accounts/facebook/login/")

    return redirect("/accounts/facebook/login/")

def get_cart_items(user):
    """ Fetch all cart items for a user """
    cart_items = CartItem.objects.filter(user__user_id=user.user_id).select_related("dish", "restaurant")

    return [
        {
            "dishId": item.dish.dish_id,
            "dishName": item.dish.dish_name,
            "price": float(item.dish.price),
            "quantity": item.quantity,
            "restaurantId": item.restaurant.rest_id if item.restaurant else None,
            "restaurantName": item.restaurant.name if item.restaurant else "Unknown",
            "photo": item.dish.photo.url if item.dish.photo else None,
        }
        for item in cart_items
    ]



@login_required
@csrf_exempt  # ✅ Ensure CSRF token is sent in JavaScript for security
def add_to_cart(request):
    """ Adds an item to the cart and handles errors properly """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Only POST allowed."}, status=400)

    try:
        # ✅ Parse request body and log received data
        data = json.loads(request.body)
        logger.info(f"📥 Received add_to_cart request: {data}")

        dish_id = data.get("dishId")
        restaurant_id = data.get("restaurantId")
        quantity = data.get("quantity", 1)

        if not dish_id or not restaurant_id:
            logger.error(f"❌ Missing dish_id ({dish_id}) or restaurant_id ({restaurant_id})")
            return JsonResponse({"error": "Missing dish ID or restaurant ID."}, status=400)

        if not isinstance(quantity, int) or quantity < 1:
            logger.error(f"❌ Invalid quantity received: {quantity}")
            return JsonResponse({"error": "Quantity must be a positive integer."}, status=400)

        # ✅ Convert IDs safely
        try:
            dish_id = int(dish_id)
            restaurant_id = int(restaurant_id)
            quantity = int(quantity)
        except ValueError:
            logger.error("❌ Invalid ID conversion.")
            return JsonResponse({"error": "Invalid data format. Dish ID and Restaurant ID must be integers."}, status=400)

        user_id = request.user.user_id
        user = get_object_or_404(CustomUser, user_id=user_id)

        # ✅ Ensure restaurant exists
        restaurant = get_object_or_404(Restaurant, rest_id=restaurant_id)
        logger.info(f"✅ Found restaurant: {restaurant.name} (ID: {restaurant_id})")

        # ✅ Ensure dish exists in the selected restaurant
        dish = Dish.objects.filter(dish_id=dish_id, restaurants=restaurant).first()
        if not dish:
            logger.error(f"❌ Dish ID {dish_id} not found in restaurant ID {restaurant_id}")
            return JsonResponse({"error": "Dish does not exist in the selected restaurant."}, status=404)

        # ✅ Ensure CartItem exists or create a new one
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                user_id=user_id,
                dish=dish,
                restaurant=restaurant,
                defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        logger.info(f"✅ Added to cart: {dish.dish_name} x {quantity} for {user.username}")

        return JsonResponse({"message": "Item added successfully", "cart": get_cart_items(request.user)}, status=200)


    except json.JSONDecodeError:
        logger.error("❌ JSON Decode Error: Invalid JSON format received.")
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        logger.error(f"🔥 Unexpected error in add_to_cart:\n{traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected error occurred. Check server logs."}, status=500)
    

def get_cart(request):
    """Retrieve all cart items for the logged-in user and update the cart badge dynamically."""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"cart": [], "message": "User not logged in."}, status=200)

        cart_items = CartItem.objects.filter(user=request.user).select_related("dish", "restaurant")

        cart_data = [
            {
                "dishId": item.dish.dish_id if item.dish else None,
                "dishName": item.dish.dish_name if item.dish else "Unknown",
                "price": float(item.dish.price) if item.dish else 0.00,
                "quantity": item.quantity,
                "restaurantId": item.restaurant.rest_id if item.restaurant else None,
                "restaurantName": item.restaurant.name if item.restaurant else "Unknown",
                "photo": request.build_absolute_uri(item.dish.photo.url) if item.dish and item.dish.photo else None,
            }
            for item in cart_items
        ]

        return JsonResponse({"cart": cart_data, "cartItemCount": sum(item["quantity"] for item in cart_data)}, status=200)

    except Exception as e:
        logger.error(f"🔥 Unexpected error in get_cart:\n{traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected error occurred while retrieving cart items."}, status=500)


@login_required
@csrf_exempt
def remove_from_cart(request):
    """ Remove an item from the cart for a specific restaurant """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        dish_id = data.get("dishId")
        restaurant_id = data.get("restaurantId")

        if not dish_id or not restaurant_id:
            return JsonResponse({"error": "Dish ID and Restaurant ID are required."}, status=400)

        try:
            dish_id = int(dish_id)
            restaurant_id = int(restaurant_id)
        except ValueError:
            return JsonResponse({"error": "Invalid data format."}, status=400)

        user = request.user

        # ✅ Ensure restaurant and dish exist
        restaurant = get_object_or_404(Restaurant, rest_id=restaurant_id)
        dish = get_object_or_404(Dish, dish_id=dish_id, restaurants=restaurant)

        # ✅ Find and delete the cart item
        cart_item = CartItem.objects.filter(user=user, dish=dish, restaurant=restaurant).first()
        if not cart_item:
            return JsonResponse({"error": "Item not found in cart."}, status=404)

        cart_item.delete()

        return JsonResponse({"message": "Item removed successfully.", "cart": get_cart_items(request.user)})


    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        logger.error(f"🔥 Error in remove_from_cart:\n{traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)




@login_required
@csrf_exempt
def empty_cart(request):
    """ Remove all items from the user's cart """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        user = request.user
        deleted_count, _ = CartItem.objects.filter(user=user).delete()

        return JsonResponse({"message": "Cart emptied successfully", "cart": [] if deleted_count else []})

    except Exception as e:
        logger.error(f"🔥 Unexpected error in empty_cart: {traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)
    

@login_required
@csrf_exempt  # ✅ Ensure CSRF is handled in JavaScript
def update_cart(request):
    """ Updates the quantity of an existing cart item """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Only POST allowed."}, status=400)

    try:
        # ✅ Parse request body and log received data
        data = json.loads(request.body)
        logger.info(f"📥 Received update_cart request: {data}")

        dish_id = data.get("dishId")
        restaurant_id = data.get("restaurantId")
        quantity = data.get("quantity")

        if not dish_id or not restaurant_id or not isinstance(quantity, int) or quantity < 1:
            logger.error(f"❌ Invalid input: {data}")
            return JsonResponse({"error": "Invalid input. Quantity must be at least 1."}, status=400)

        user_id = request.user.user_id

        # ✅ Fetch existing cart item
        cart_item = CartItem.objects.filter(
            user_id=user_id,
            dish_id=dish_id,
            restaurant_id=restaurant_id
        ).first()

        if not cart_item:
            logger.error(f"❌ CartItem not found: Dish {dish_id}, Restaurant {restaurant_id}, User {user_id}")
            return JsonResponse({"error": "Item not found in cart"}, status=404)

        # ✅ Update quantity
        cart_item.quantity = quantity
        cart_item.save()

        logger.info(f"✅ Updated cart item: {cart_item.dish.dish_name} x {quantity} for user {user_id}")

        return JsonResponse({"message": "Cart updated successfully", "cart": get_cart_items(request.user)}, status=200)

    except json.JSONDecodeError:
        logger.error("❌ JSON Decode Error: Invalid JSON format received.")
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        logger.error(f"🔥 Unexpected error in update_cart:\n{traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected error occurred. Check server logs."}, status=500)

def cart_item_count(request):
    """ Returns the total number of items in the user's cart. """
    if request.user.is_authenticated:
        total_items = CartItem.objects.filter(user=request.user).aggregate(total_qty=Sum("quantity"))["total_qty"] or 0
        print(f"🛒 DEBUG: Cart item count = {total_items}")  # Debugging line
        return {"cart_item_count": total_items}
    return {"cart_item_count": 0}



@login_required
def checkout(request):
    user = request.user
    user_details, created = UserDetails.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "🛒 Your cart is empty.")
        return redirect('home')

    # Check required fields
    missing_fields = []
    if not user_details.address:
        missing_fields.append("Address")
    if not user_details.phone:
        missing_fields.append("Phone")
    if not user_details.allergies:
        missing_fields.append("Allergies")

    if missing_fields:
        messages.warning(request, f"⚠️ Please complete your profile before checkout: {', '.join(missing_fields)}")
        return redirect('/#profileSection')

    # ✅ All good → Redirect to summary page (checkout app)
    return redirect('checkout:order_summary')


class PlatformDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_db'

    #def ready(self):
    #    import platform_db.signals

    
@login_required
def redirect_after_login(request):
    if request.user.is_restaurant:
        return redirect(reverse('dish_list'))  # dish_list -> name from restaurant_manager urls.py
    return redirect('/')  # normal users → home page


# Check if user is delivery personnel
def is_delivery(user):
    return user.is_authenticated and user.is_delivery


# Delivery Personnel → See My Claimed Orders
@login_required
@user_passes_test(is_delivery)
def delivery_dashboard(request):
    # My claimed orders (not delivered yet)
    my_orders = DeliveryOrder.objects.filter(delivery=request.user).exclude(status='delivered')

    # My delivered orders
    delivered_orders = DeliveryOrder.objects.filter(delivery=request.user, status='delivered')

    # Available orders to claim (not claimed yet by anyone)
    claimed_ids = DeliveryOrder.objects.values_list('purchase_id', flat=True)
    available_orders = Purchase.objects.exclude(purch_id__in=claimed_ids)

    context = {
        'my_orders': my_orders,
        'delivered_orders': delivered_orders,
        'available_orders': available_orders,
    }
    return render(request, 'platform_db/delivery_dashboard.html', context)


# Claim specific order
@login_required
@user_passes_test(is_delivery)
def claim_order(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    if DeliveryOrder.objects.filter(purchase=purchase).exists():
        messages.warning(request, "Order already claimed!")
    else:
        DeliveryOrder.objects.create(purchase=purchase, delivery=request.user)
        messages.success(request, "Order claimed successfully!")

    return redirect('platform_db:delivery_dashboard')



# Update delivery status
@login_required
@user_passes_test(is_delivery)
def update_delivery_status(request, order_id, new_status):
    order = get_object_or_404(DeliveryOrder, id=order_id, delivery=request.user)
    order.status = new_status
    order.save()
    return redirect('platform_db:delivery_dashboard')


@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserSignupForm()

    return render(request, 'platform_db/signup.html', {'form': form})