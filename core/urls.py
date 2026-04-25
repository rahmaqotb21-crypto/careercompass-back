from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/test/', include('skill_test.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/careers/', include('careers.urls')),
]