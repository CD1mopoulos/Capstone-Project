from django.urls import path
from . import views


app_name = 'contact' 

urlpatterns = [
    path('', views.contact, name='contact'),
    path('submit_comment/', views.submit_comment, name='submit_comment'),
    path('send/', views.send_contact_email, name='send_contact_email'),
]
