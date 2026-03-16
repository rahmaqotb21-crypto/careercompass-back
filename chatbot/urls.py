from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ChatbotView.as_view(), name='chat'),
    path('history/<int:session_id>/', views.ChatHistoryView.as_view(), name='chat-history'),
]