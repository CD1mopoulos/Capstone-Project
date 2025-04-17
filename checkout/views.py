from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from platform_db.models import UserDetails, Purchase, PurchasedDish, CartItem
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
import json
import requests


@login_required
def order_summary(request):
    user = request.user
    user_details = UserDetails.objects.get(user=user)

    # ✅ Use live cart items instead of previous purchases
    cart_items = CartItem.objects.filter(user=user).select_related('dish')

    if not cart_items.exists():
        messages.warning(request, "🛒 Your cart is empty.")
        return redirect('home')

    total_price = sum(item.quantity * item.dish.price for item in cart_items)

    return render(request, 'checkout/order_summary.html', {
        'user_details': user_details,
        'purchased_items': cart_items,  # still use this key in the template
        'total_price': total_price,
        'user': user,
        'purchase': None  # in case your template expects this key
    })


@login_required
def delete_order(request, purchase_id):
    if purchase_id == 0:
        # Just clear the cart
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "🗑️ Cart cleared successfully.")
        return redirect('home')

    # Otherwise delete the specific purchase
    purchase = Purchase.objects.filter(purch_id=purchase_id, user=request.user).first()
    if purchase:
        PurchasedDish.objects.filter(purchase=purchase).delete()
        purchase.delete()
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "🗑️ Order and cart cleared successfully.")

    return redirect('home')


@require_POST
@login_required
def update_payment(request):
    user_details = UserDetails.objects.get(user=request.user)
    new_method = request.POST.get("payment_method")

    # Include all valid options
    valid_methods = ["cash_on_delivery", "card", "paypal"]

    if new_method in valid_methods:
        user_details.payment_method = new_method
        user_details.save()
        messages.success(request, "✅ Payment method updated.")
    else:
        messages.warning(request, "❌ Invalid payment method.")

    return redirect('checkout:order_summary')


@require_POST
@login_required
def complete_order(request):
    user = request.user
    user_details, created = UserDetails.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "🛒 Your cart is empty.")
        return redirect('home')

    # Build order summary and total price
    order_summary = "\n".join([
        f"{item.quantity} x {item.dish.dish_name} (€{item.dish.price})"
        for item in cart_items
    ])
    total_price = sum(item.quantity * item.dish.price for item in cart_items)

    # Step 1: Create Purchase
    purchase = Purchase.objects.create(user=user)

    # Step 2: Create Purchased Dishes
    for item in cart_items:
        PurchasedDish.objects.create(purchase=purchase, dish=item.dish, quantity=item.quantity)

    # ⚠️ No Auto-Assign here anymore → Delivery Personnel will claim manually!

    # Step 3: Send Confirmation Email
    subject = 'Your Order Confirmation'
    message = render_to_string('checkout/order_confirmation_email.txt', {
        'name': user_details.name or user.first_name,
        'surname': user_details.surename or user.last_name,
        'address': user_details.address,
        'phone': user_details.phone,
        'order_summary': order_summary,
        'allergies': user_details.allergies,
        'total_price': total_price,
        'payment_method': user_details.payment_method,
    })

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

    # Step 4: Clear Cart
    cart_items.delete()

    # Step 5: Success Message
    messages.success(request, "🎉 Your order has been completed!")

    return redirect('home')



@require_POST
@login_required
def update_address(request):
    user_details = UserDetails.objects.get(user=request.user)
    new_address = request.POST.get("address")
    if new_address:
        user_details.address = new_address
        user_details.save()
    return redirect('checkout:order_summary')



@csrf_exempt
@require_POST
@login_required
def paypal_complete(request):
    data = json.loads(request.body)
    user = request.user

    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.quantity * item.dish.price for item in cart_items)

    if not cart_items.exists():
        return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

    # Save order
    purchase = Purchase.objects.create(user=user)
    for item in cart_items:
        PurchasedDish.objects.create(purchase=purchase, dish=item.dish, quantity=item.quantity)

    # Update payment method
    user_details, _ = UserDetails.objects.get_or_create(user=user)
    user_details.payment_method = "paypal"
    user_details.save()

    cart_items.delete()

    return JsonResponse({'status': 'success'})

def thank_you(request):
    return render(request, 'checkout/thank_you.html')


@login_required
@csrf_exempt
def initiate_paypal_redirect(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.quantity * item.dish.price for item in cart_items)

    if not cart_items.exists():
        return redirect('checkout:order_summary')  # ✅ fixed name

    PAYPAL_CLIENT_ID = 'AS05H7zrih3eDrM-cbRDVRtZYAjpfhFTL3in7z9tivClRPyhAF8zuSybkG9vzg-caXlLR_zHAn4GKPHg'
    PAYPAL_SECRET = 'EG3rKb72_5Y6mwVCTwuaZPCWoCOD2IigeJvteVkG2JufFfqm4_6h3mygP2bHEoc6_puLLTfkJLPcibzV'
    PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'

    # Get access token
    auth_response = requests.post(
        f'{PAYPAL_API_BASE}/v1/oauth2/token',
        headers={"Accept": "application/json"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    ).json()

    token = auth_response['access_token']

    # Create PayPal order
    order_response = requests.post(
        f'{PAYPAL_API_BASE}/v2/checkout/orders',
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "EUR",
                    "value": f"{total_price:.2f}"
                }
            }],
            "application_context": {
                "return_url": request.build_absolute_uri(reverse('checkout:paypal_return')),
                "cancel_url": request.build_absolute_uri(reverse('checkout:order_summary'))
            }
        }
    ).json()

    for link in order_response['links']:
        if link['rel'] == 'approve':
            return redirect(link['href'])

    # Fallback if approval link is missing
    return redirect('checkout:order_summary')

from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@login_required
@csrf_exempt
def paypal_return(request):
    order_id = request.GET.get('token')
    payer_id = request.GET.get('PayerID')

    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "🛒 Your cart is empty.")
        return redirect('home')

    # Save purchase
    purchase = Purchase.objects.create(user=user)
    order_summary = ""
    total_price = 0

    for item in cart_items:
        PurchasedDish.objects.create(purchase=purchase, dish=item.dish, quantity=item.quantity)
        subtotal = item.quantity * item.dish.price
        total_price += subtotal
        order_summary += f"{item.quantity} × {item.dish.dish_name} (€{item.dish.price}) — €{subtotal:.2f}\n"

    # Update user details
    user_details, _ = UserDetails.objects.get_or_create(user=user)
    user_details.payment_method = "paypal"
    user_details.save()

    # Send confirmation email
    subject = 'Your Order Confirmation'
    message = render_to_string('checkout/order_confirmation_email.txt', {
        'name': user_details.name or user.first_name,
        'surname': user_details.surename or user.last_name,
        'address': user_details.address,
        'phone': user_details.phone,
        'order_summary': order_summary,
        'allergies': user_details.allergies,
        'total_price': total_price,
        'payment_method': user_details.payment_method,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

    # Clear the cart
    cart_items.delete()

    return redirect('checkout:thank_you')
