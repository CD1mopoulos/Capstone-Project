"""
URL configuration for NomNomNow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Load the home page from the home app
    path('contact/', include('contact.urls')),
    #path('', include('platform_db.urls')),
    path('finish_order/', include('finish_order.urls')),
    path('accounts/', include('allauth.urls')),  # Load allauth urls 
    path('platform_db/', include('platform_db.urls')),
    path('about/', include('aboutus.urls')),
    path('checkout/', include('checkout.urls')),
    path('search/', include('search.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('restaurant/', include('restaurant_manager.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve media files during development if in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
