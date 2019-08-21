from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
    path('cart/', TemplateView.as_view(template_name='core/cart.html'), name="cart"),
    path('profile/', TemplateView.as_view(template_name='core/profile.html'), name="profile"),
    path('cart/<pk>/', views.ListShoppingCart.as_view(), name="cart"),
    path('dashboard/ajax/getarticle/', views.obtenerarticulo, name='obtenerarticulo'),
]
