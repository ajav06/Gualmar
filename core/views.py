from django.shortcuts import render
from django.views.generic import ListView

from . import models

# Create your views here.

class DashboardViews(ListView):
    model = models.Article
    template_name='core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = models.CategoryArticle.objects.all()
        return context
