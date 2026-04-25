from django.urls import path
from . import views

urlpatterns = [
    path('', views.CareerListView.as_view(), name='career-list'),
    path('<int:career_id>/', views.CareerDetailView.as_view(), name='career-detail'),
]