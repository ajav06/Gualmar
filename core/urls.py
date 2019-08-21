from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', LoginView.as_view()),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
    path('cart/<pk>/', views.ListShoppingCart.as_view(), name="cart"),
    path('dashboard/ajax/getarticle/', views.obtenerarticulo, name='obtenerarticulo'),
]
