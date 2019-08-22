from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView
from django.forms import Form
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from .models import Article, Address, User, ShoppingCart

from . import models

# Create your views here.

class DashboardViews(CreateView):
    """ Patalla de Inicio """
    model = models.Search
    fields = '__all__'
    template_name = "core/dashboard.html"
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = redirect(reverse_lazy('search'))
        formu = form.save(commit=False)
        if formu.phrase:
            response.set_cookie('search-phrase', formu.phrase, path='/search/')
        else:
            response.set_cookie('search-phrase', '', path='/search/')
        if formu.category:
            response.set_cookie('search-category', formu.category, path='/search/')
        else:
            response.set_cookie('search-category', '--', path='/search/')
        
        search = models.Search()
        search.phrase = formu.phrase
        search.category = formu.category
        search.id_session = self.request.COOKIES['sessionid']
        search.user = self.request.user
        search.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = models.Article.objects.all()
        context['categories'] = models.CategoryArticle.objects.all().order_by('name')
        return context

def obtenerarticulo(request):
    """ Función para mostrar información 
        de un Artículo en una modal """
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

def añadircarrito(request):
    """ Función que añade un artículo al carrito
        de compras de un usuario """
    codigoart = request.POST.get('codigo', None)
    if not codigoart:
        codigoart = 1
    articulo = Article.objects.get(code=codigoart)
    user = request.user    
    sc = ShoppingCart()
    sc.user = user
    sc.article = articulo
    sc.quantity = 1
    sc.amount = articulo.price
    try:
        sc.save()
        return JsonResponse({'exito':True})
    except:
        return JsonResponse({'exito':False})

def eliminarcarrito(request):
    """ Función que elimina un item del
        carrito de compras """
    try:
        codigocarrito = request.POST.get('codigo', None)
        if not codigocarrito:
            codigocarrito = 1
        carrito = ShoppingCart.objects.get(id = codigocarrito)
        carrito.delete()
        return JsonResponse({'exito':True})
    except:
        return JsonResponse({'exito':False})

class ListShoppingCart(ListView):
    """ Lista de Carrito de Compra por Usuario """
    model = models.ShoppingCart
    template_name = 'core/cart.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["carts"] = models.ShoppingCart.objects.filter(user__id=user.id)
        if context["carts"]:
            context["hay"] = True
        else:
            context["hay"] = False
        montoT = 0
        for cart in context["carts"]:
            montoT += cart.amount
        context["total"] = round(montoT,2)
        return context

class login(LoginView):
    """ Inicio de Sesión del Usuario """
    template_name = 'registration/login.html'

class profile(DetailView):
    model = User
    template_name= 'core/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(profile, self).get_context_data(**kwargs)
        context['direccion'] = Address.objects.get(user = self.request.user.id)
        return context

class SearchView(ListView):
    """ Página de Búsqueda """ 
    model = models.Article
    template_name = "core/search.html"  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phrase = self.request.COOKIES['search-phrase']
        category = self.request.COOKIES['search-category']
        context["articles"] = models.Article.objects.filter(name__contains=phrase)
        if category == '--':
            context["categories"] = models.CategoryArticle.objects.all()
        else:
            context["categories"] = models.CategoryArticle.objects.filter(id=category)
        return context
    
        
def payments(request):
    return render(request, 'core/payments.html', {})

def purchases(request):
    return render(request, 'core/purchases.html', {})

