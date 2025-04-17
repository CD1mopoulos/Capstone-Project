from django.urls import path
from . import views

urlpatterns = [
    path('results/', views.search_results, name='search_results'),
]
