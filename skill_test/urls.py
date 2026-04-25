from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.GenerateTestView.as_view(), name='generate-test'),
    path('submit/', views.SubmitTestView.as_view(), name='submit-test'),
]