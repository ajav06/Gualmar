from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView
from django.forms import Form
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from .models import Article, Address, User, ShoppingCart, Bill, BillDetails, PaymentDetails, ArticleClick
import random
from django.core import serializers
from django.shortcuts import redirect
from datetime import datetime
import time

from . import models

# Create your views here.

class LastAccessMixin(object):
    def dispatch(self, request, *args, **kwargs):
        request.user.last_access = datetime.now()
        request.user.save(update_fields=['last_access'])
        return super(LastAccessMixin, self).dispatch(request, *args, **kwargs)

def dashboard_checker(request):
    if (request.user.last_login.date()-request.user.last_access.date()).days != 0:
        return redirect('/cart/')
    else:
        return redirect('/dashboard/')

class logout(LastAccessMixin, LogoutView):
    template_name = 'whatever xd'

class DashboardViews(CreateView):
    """ Patalla de Inicio """
    model = models.Search
    fields = '__all__'
    template_name = "core/dashboard.html"
    success_url = reverse_lazy('search')
    frase = None
    categoria = None
    contexto_busqueda = dict()

    def form_valid(self, form):
        response = redirect(reverse_lazy('search'))
        formu = form.save(commit=False)
        if formu.phrase:
            response.set_cookie('search-phrase', formu.phrase)
        else:
            response.set_cookie('search-phrase', '')
        if formu.category:
            response.set_cookie('search-category', formu.category)
        else:
            response.set_cookie('search-category', '-1')
        
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
    click = ArticleClick()
    click.user = request.user
    click.article = articulo
    click.save()
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

def pagar(request):
    """ Función que simula el pago """
    try:
        usuario = request.user
        #Primero, cargo sus artículos del carrito de compras
        carrito = ShoppingCart.objects.filter(user=usuario)
        #Calculo el monto total a pagar
        monto = 0
        for articulo in carrito:
            monto += articulo.amount
        monto = round(monto,2)
        #Luego, el tipo de pago (quiero crear la factura)
        tipo_pago = request.POST.get('tipo', None)
        #Creo el detalle de pago:
        dp = PaymentDetails()
        dp.user = usuario
        dp.payment_type = tipo_pago
        dp.transaction_code = str(random.randrange(0,99999999)).zfill(8)
        dp.status = 'e'
        dp.save()
        #Creo la factura:
        factura = Bill()
        factura.user = usuario
        factura.amount = monto
        factura.address = Address.objects.get(user=usuario)
        factura.status = 'a'
        factura.payment = dp
        factura.save()
        #Creo los detalle de factura
        for articulo in carrito:
            detfact = BillDetails()
            detfact.bill = factura
            detfact.article = articulo.article
            detfact.quantity = articulo.quantity
            detfact.amount = articulo.amount
            detfact.save()
        #Limpio el carrito
        carrito.delete()        
        #Listo. Devuelvo que el pago fue exitoso
        return JsonResponse({'exito':True})
    except:
        return JsonResponse({'exito':False})

def detallefactura(request):
    """ Consulta el detalle de una factura """
    id_fact = request.POST.get('id')
    detfacturas = BillDetails.objects.filter(bill_id=id_fact)
    df = [{}]
    for detalle in detfacturas:
        d = {
            'articulo':detalle.article.name,
            'foto':detalle.article.image.url,
            'monto':detalle.amount
        }
        df.append(d)
    return JsonResponse(df,safe=False)

class ListShoppingCart(ListView):
    """ Lista de Carrito de Compra por Usuario """
    model = models.ShoppingCart
    template_name = 'core/cart.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        #time.sleep(0.5)
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
        frase = self.request.COOKIES['search-phrase']
        categoria = self.request.COOKIES['search-category']
        cat = int(categoria)
        if cat == -1:
            context['categories'] = models.CategoryArticle.objects.all().order_by('name')
            context['articles'] = models.Article.objects.filter(name__contains=frase) | models.Article.objects.filter(description__contains=frase)
            context['articles'] = context['articles'].distinct()
            categorias = []
            for article in context['articles']:
                for categ in article.categories.all().order_by('name'):
                    category = models.CategoryArticle.objects.get(id=categ.id)
                    if category and category not in categorias:
                        categorias.append(category)
            context['categories'] = categorias
        else:
            context['categories'] = models.CategoryArticle.objects.all().filter(id=categoria).order_by('name')
            context['articles'] = models.Article.objects.filter(name__contains=frase) | models.Article.objects.filter(description__contains=frase)
            context['articles'] = context['articles'].distinct()
        return context
    
        
def payments(request):
    return render(request, 'core/payments.html', {})

class purchases(ListView):
    model = Bill
    template_name = 'core/purchases.html'

    def get_context_data(self, **kwargs):
        context = super(purchases, self).get_context_data(**kwargs)
        context['object_list'] = Bill.objects.filter(user=self.request.user.id).order_by('-id')
        return context

