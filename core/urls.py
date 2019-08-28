from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.login.as_view(), name="login"),
    path('checker/', views.dashboard_checker, name="checker"),
    path('logout/', views.logout.as_view(), name="logout"),
    path('signup/', views.signup.as_view(), name="signup"),
    path('dashboard/', views.DashboardViews.as_view(), name="dashboard"),
    path('profile/', views.profile.as_view(template_name='core/profile.html'), name="profile"),
    path('cart/', views.ListShoppingCart.as_view(), name="cart"),
    path('search/', views.SearchView.as_view(), name="search"),
    path('payments/', views.payments.as_view(), name="payments"),
    path('purchases/', views.purchases.as_view(), name="purchases"),
    path('payments/ajax/pay/', views.AjaxViews.pagar, name='pagar'),
    path('purchases/ajax/detail/', views.AjaxViews.detallefactura, name='detfact'),
    path('dashboard/ajax/getarticle/', views.AjaxViews.obtenerarticulo, name='obtenerarticulo'),
    path('dashboard/ajax/addarticle/', views.AjaxViews.añadircarrito, name='añadircarrito'),
    path('cart/ajax/getarticle/', views.AjaxViews.obtenerarticulo, name='obtenerarticulo'),
    path('cart/ajax/removearticle/', views.AjaxViews.eliminarcarrito, name='eliminarcarrito'),
    path('cart/ajax/recomendaciones/', views.AjaxViews.recomendaciones, name='recomendaciones'),
    path('cart/ajax/limpiar/', views.AjaxViews.limpiarcarrito, name='limpiarcarrito'),
    path('search/ajax/getarticle/', views.AjaxViews.obtenerarticulo, name='obtenerarticuloS'),
    path('search/ajax/addarticle/', views.AjaxViews.añadircarrito, name='añadircarritoS'),
]
