from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from .models import Article

from . import models

# Create your views here.

class DashboardViews(ListView):
    model = models.Article
    template_name='core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = models.Article.objects.all()
        context['categories'] = models.CategoryArticle.objects.all()
        return context

def obtenerarticulo(request):
    codigo = request.POST.get('codigo', None)
    if codigo:
        articulo = Article.objects.get(code=codigo)
    else:
        articulo = Article.objects.get(code=1)
    data = {
        'nombre' : articulo.name,
        'descripcion' : articulo.description,
        'precio' : articulo.price,
        'image' : articulo.image.url,
    }
    return JsonResponse(data)

class login(LoginView):
    template_name = 'registration/login.html'