from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ChatbotView.as_view(), name='chat'),
    path('sessions/', views.ChatSessionsView.as_view(), name='chat-sessions'),
    path('history/<int:session_id>/', views.ChatHistoryView.as_view(), name='chat-history'),
    path('plan-status/', views.PlanStatusView.as_view(), name='plan-status'),
]