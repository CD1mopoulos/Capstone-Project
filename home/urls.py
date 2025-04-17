from django.urls import path
from home import views

urlpatterns = [
    path('', views.rec_dish, name='home'),  # 👈 your personalized home page
    path('terms/', views.terms_conditions, name='terms_conditions'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]
