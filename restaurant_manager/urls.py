from django.urls import path
from . import views

urlpatterns = [
    path('dishes/', views.dish_list, name='dish_list'),
    path('dishes/add/', views.dish_add, name='dish_add'),
    path('dishes/edit/<int:pk>/', views.dish_edit, name='dish_edit'),
    path('dishes/delete/<int:pk>/', views.dish_delete, name='dish_delete'),
]
