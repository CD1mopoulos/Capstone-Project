from django.urls import path
from .views import cart_view, checkout_view

app_name = "finish_order"

urlpatterns = [
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
]
