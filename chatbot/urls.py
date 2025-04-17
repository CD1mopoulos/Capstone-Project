from django.urls import path
from .views import chatbot_response, chatbot_widget

urlpatterns = [
    path("", chatbot_response, name="chatbot_response"),
    path("chatbot-widget/", chatbot_widget, name="chatbot_widget"),
]
