from django.urls import path
from .views import ChatbotView, ChatHistoryView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('history/<int:session_id>/', ChatHistoryView.as_view(), name='chat_history'),
]