from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from . import views
from .views import profile

urlpatterns = [
    path('', views.login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
    path('profile/', profile.as_view(template_name='core/profile.html'), name="profile"),
    path('cart/', views.ListShoppingCart.as_view(), name="cart"),
    path('search/', views.SearchView.as_view(), name="search"),
    path('payments/', views.payments, name="payments"),
    path('purchases/', views.purchases.as_view(), name="purchases"),
    path('payments/ajax/pay/', views.pagar, name='pagar'),
    path('purchases/ajax/detail/', views.detallefactura, name='detfact'),
    path('dashboard/ajax/getarticle/', views.obtenerarticulo, name='obtenerarticulo'),
    path('dashboard/ajax/addarticle/', views.añadircarrito, name='añadircarrito'),
    path('cart/ajax/getarticle/', views.obtenerarticulo, name='obtenerarticulo'),
    path('cart/ajax/removearticle/', views.eliminarcarrito, name='eliminarcarrito'),
    path('search/ajax/getarticle/', views.obtenerarticulo, name='obtenerarticuloS'),
    path('search/ajax/addarticle/', views.añadircarrito, name='añadircarritoS'),
]
