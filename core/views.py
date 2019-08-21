from django.shortcuts import render
from django.views.generic import ListView
from django.http import JsonResponse
from .models import Article

from . import models

# Create your views here.

class DashboardViews(ListView):
    model = models.Article
    template_name='core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = models.CategoryArticle.objects.all()
        return context

def obtenerarticulo(request):
    codigo = request.POST.get('codigo', None)
    articulo = Article.objects.get(code=codigo)
    data = {
        'nombre' : articulo.name,
        'descripcion' : articulo.descripcion,
        'precio' : articulo.price,
        'categoria' : articulo.categories,
        'image' : articulo.image.url,
    }
    return JsonResponse(data)