from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', LoginView.as_view()),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
]
