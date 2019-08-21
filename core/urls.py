from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', LoginView.as_view()),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
    path('cart/', TemplateView.as_view(template_name='core/cart.html'), name="cart"),
    path('profile/', TemplateView.as_view(template_name='core/profile.html'), name="profile"),
    path('ajax/getarticle/', views.obtenerarticulo, name='obtenerarticulo'),
]
