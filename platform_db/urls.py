from django.urls import path, include
from django.contrib.auth import views as auth_views
from platform_db.views import (
    signup_view,        # Mobile normal signup
    signup,             # Modal (AJAX) signup
    user_login,         # Mobile login
    complete_signup,
    update_profile,
    add_to_cart,
    remove_from_cart,
    custom_logout,
    empty_cart,
    update_cart,
    get_menu,
    redirect_after_login,
    restaurant_list,
    get_cart,
    get_nearby_restaurants,
    delivery_dashboard,
    claim_order,
    update_delivery_status,
    checkout
)

app_name = 'platform_db'

urlpatterns = [
    # Restaurants
    path('restaurants/', restaurant_list, name='restaurant-list'),

    # Mobile Login / Signup
    path('login/', user_login, name='user_login'),
    path('signup/', signup_view, name='signup'),

    # AJAX Signup (Modals)
    path('ajax-signup/', signup, name='ajax_signup'),

    # Allauth Login/Signup (Google, Facebook)
    path('accounts/', include('allauth.urls')),

    # Logout
    path('logout/', custom_logout, name='logout'),

    # Menus / Cart
    path('get-menu/<int:rest_id>/', get_menu, name='get_menu'),
    path('complete-signup/', complete_signup, name='complete_signup'),
    path('update-profile/', update_profile, name='update_profile'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/get/', get_cart, name='get_cart'),
    path('cart/empty/', empty_cart, name='empty_cart'),
    path('cart/update/', update_cart, name='update_cart'),

    # Extras
    path('get_nearby_restaurants/', get_nearby_restaurants, name='get_nearby_restaurants'),
    path('redirect-after-login/', redirect_after_login, name='redirect_after_login'),

    # Checkout
    path('checkout/', checkout, name='checkout'),

    # Delivery Personnel
    path('delivery/dashboard/', delivery_dashboard, name='delivery_dashboard'),
    path('delivery/claim-order/<int:purchase_id>/', claim_order, name='claim_order'),
    path('delivery/update-status/<int:order_id>/<str:new_status>/', update_delivery_status, name='update_delivery_status'),

    path('login/', auth_views.LoginView.as_view(template_name='platform_db/login.html'), name='account_login'),
]
