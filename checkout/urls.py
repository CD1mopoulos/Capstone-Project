from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('summary/', views.order_summary, name='order_summary'),
    path('delete/<int:purchase_id>/', views.delete_order, name='delete_order'),
    path('update-payment/', views.update_payment, name='update_payment'),
    path('complete/', views.complete_order, name='complete_order'),
    path('update-address/', views.update_address, name='update_address'),
    path('paypal-complete/', views.paypal_complete, name='paypal_complete'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('paypal-redirect/', views.initiate_paypal_redirect, name='initiate_paypal_redirect'),
    path('paypal-return/', views.paypal_return, name='paypal_return'),
]
