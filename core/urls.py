from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/login.html')),
    path('dashboard/', TemplateView.as_view(template_name='core/dashboard.html'), name="dashboard"),
]