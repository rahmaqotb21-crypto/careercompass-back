from django.urls import path
from .views import LearningPlanDetailView, LearningPlanLatestView, LearningPlanListView

urlpatterns = [
    path('', LearningPlanListView.as_view(), name='learning-plan-list'),
    path('latest/', LearningPlanLatestView.as_view(), name='learning-plan-latest'),
    path('<int:session_id>/', LearningPlanDetailView.as_view(), name='learning-plan-detail'),
]