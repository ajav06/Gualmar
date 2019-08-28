import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from core.models import Search, User, Article, CategoryArticle, ArticleClick, Bill, BillDetails, ShoppingCart
from datetime import datetime
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from core.views import recomiendame, dashboard, DashboardViews
from django.db.models.signals import post_save
import random

class AgenteGualmar(Agent): ##El Agente
    ult_busqueda = Search.objects.all().order_by('-id')
    if ult_busqueda:
        ult_busqueda = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda
    else:
        ult_busqueda = None
    ult_click = ArticleClick.objects.all().order_by('-id')
    if ult_click:
        ult_click = ArticleClick.objects.all().order_by('-id')[0] ##Guarda el último click
    else:
        ult_click = None
    ult_compra = Bill.objects.all().order_by('-id') ##Guarda la última factura al momento de iniciar el servidor
    if ult_compra:
        ult_compra = Bill.objects.all().order_by('-id')[0]
    else:
        ult_compra = None
    tabla_interes = [] ##Instancia una tabla de interés, vacía, que luego llenará con datos de cada usuario

    ## COMPORTAMIENTOS
    ## 1) Comportamiento que inicializa la tabla y que monitorea nuevas búsquedas/clicks.

    class MonitorBusquedasClicks(CyclicBehaviour):
        async def on_start(self): ##Cuando se ejecuta, quiero que inicialice la tabla.
            for usuario in User.objects.all().order_by('id'): ##Por cada usuario, realiza lo siguiente:
                categorias = dict() ##Crea un diccionario que guardará las categorías.
                articulosd = dict() ##Crea un diccionario que guardará los artículos.
                for categoria in CategoryArticle.objects.all(): ##Carga el diccionario con las categorías,
                    categorias[categoria] = 0 ##en interés 0. 
                busquedas = Search.objects.filter(user_id=usuario.id) ##Obtiene todas sus búsquedas,
                for busqueda in busquedas: ##Iterando sobre todas sus búsquedas,
                    palabras = busqueda.phrase ##busco su frase.
                    categoria = busqueda.category ##busco su categoría.
                    if categoria: ##Si la búsqueda tuvo categoría.
                        categorias[categoria] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Lo único que hago es incrementar el interés de la categoría por haber sido buscada.
                    if palabras: ##Si la búsqueda tuvo frases.
                        palabras = str(busqueda.phrase).split() ##consigo las frases, las divido en palabras.
                        for palabra in palabras: ##Por cada palabra,
                            categorias_añadidas = [] ##voy a guardar las categorías de estos objetos que ya he contado.
                            for articulo in (Article.objects.filter(name__contains=palabra) | Article.objects.filter(description__contains=palabra)).distinct(): ##Sobre los artículos que resultan de buscar esta palabra,
                                if not articulo in articulosd: ##Almaceno el interés en los artículos
                                    articulosd[articulo] = 0.1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Que el artículo reciba una búsqueda aumenta (poco) el interés en él
                                else:
                                    articulosd[articulo] += 0.1 / (int((datetime.now().date()-busqueda.time).days) + 1)
                                cx = articulo.categories.all() ##obtengo sus categorías,
                                for cat in cx: ##y por cada categoría del artículo,
                                    if not cat in categorias_añadidas: ##si no la he añadido ya, incremento su interés
                                        categorias[cat] += 0.5 / (int((datetime.now().date()-busqueda.time).days) + 1)
                                        categorias_añadidas.append(cat) ##Para hacerlo una sola vez por cada categoría que resulte de la búsqueda (p. ej "laptop" no suma tantas veces como computadores en tecnología, sino una sola vez)
                ##Con esto basta para tener todas las categorías por las que un usuario ha mostrado interés. Faltan los artículos.
                clicks = ArticleClick.objects.filter(user=usuario) ##Cargo todos los clicks que un usuario ha dado a un artículo
                for click in clicks: ##Ahora, cargo el interés por clicks en artículos.
                    if not click.article in articulosd: ##Cargo su interés a la tabla.
                        articulosd[click.article] = 1 / (int((datetime.now().date()-busqueda.time).days) + 1)
                    else:
                        articulosd[click.article] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1)
                for preferencia in usuario.preferences.all(): ##Me faltan sus preferencias,
                    categorias[preferencia] += 5 ##tienen un peso mayor.
                compras = Bill.objects.filter(user=usuario) ##Comprar un artículo disminuye su interés. Esto, para evitar que se recomiende un artículo recién comprado.

                for compra in compras: ##Por cada compra realizada por el usuario,
                    detalles = BillDetails.objects.filter(bill=compra) ##obtengo sus detalles,
                    for detalle in detalles: ##Itero sobre todos los detalles de factura.
                        if detalle.article in articulosd:
                            articulosd[detalle.article] -= 5 ##Disminuyo su interés en 5 (Penalización por compra)
                        else: ##ESTA PENALIZACIÓN ES ESTRICTAMENTE ARBITRARIA
                            articulosd[detalle.article] = -5 ##Establezco su interés en -5

                interes_usuario = { ##Ahora, construyo su elemento para el interes
                    'usuario': usuario.id,
                    'ult_conexion': usuario.last_login,
                    'categorias': categorias,
                    'articulos': articulosd
                }
                self.agent.tabla_interes.append(interes_usuario) ##Añado a la tabla de interés.
        
        async def run(self): ##Voy a observar las nuevas búsquedas y/o clicks.
            ub = None
            uc = None
            uo = None

            try:
                ub = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda (actual)
                uc = ArticleClick.objects.all().order_by('-id')[0] ##Guarda el último click (actual)
                uo = Bill.objects.all().order_by('-id')[0] ##Guarda la última compra.
            except:
                pass

            ##
            ## SI HAY BUSQUEDAS NUEVAS
            ##

            if self.agent.ult_busqueda != ub: ##Si detecté una nueva búsqueda...
                ultimasbusquedas = Search.objects.all().order_by('-id') ##Organizo todas las últimas búsquedas en la BD.
                busquedas_guardar = [] ##Creo un arreglo para saber cuáles voy a tomar en cuenta.
                for busqueda in ultimasbusquedas: ##Itero sobre las últimas búsquedas hasta encontrar la que era mi última.
                    if busqueda == self.agent.ult_busqueda:
                        break
                    else:
                        busquedas_guardar.append(busqueda) ##Si no he encontrado esa última búsqueda, la añado al arreglo.
                for busqueda in busquedas_guardar: ##Itero sobre el arreglo.
                    indice = int(busqueda.user.id)-1 ##Identifico al usuario en la tabla.
                    frase = busqueda.phrase ##Repito el mismo procedimiento de analizar la frase para añadir interés a los artículos.
                    categoria = busqueda.category ##Y añado interés sobre la categoría, si aplicase.
                    if frase: ##Mismo procedimiento.
                        for palabra in frase.split():
                            for articulo in (Article.objects.filter(name__contains=palabra) | Article.objects.filter(description__contains=palabra)).distinct(): 
                                categorias_añadidas = [] 
                                cx = articulo.categories.all() 
                                for cat in cx: 
                                    if not cat in categorias_añadidas: 
                                        self.agent.tabla_interes[indice]['categorias'][cat] += 0.5 
                                        categorias_añadidas.append(cat) 
                                if not articulo in self.agent.tabla_interes[indice]['articulos']: 
                                    self.agent.tabla_interes[indice]['articulos'][articulo] = 0.1 
                                else:
                                    self.agent.tabla_interes[indice]['articulos'][articulo] += 0.1
                    if categoria: ##Mismo procedimiento.
                        self.agent.tabla_interes[indice]['categorias'][categoria] += 1
                self.agent.ult_busqueda = ub
            
            ##
            ## SI HAY CLICKS NUEVOS
            ##

            if self.agent.ult_click != uc: ##Funciona similar a si hay búsquedas nuevas.
                print("Nuevo(s) click(s) detectado(s). A trabajar.")
                ultimosclicks = ArticleClick.objects.all().order_by('-id')
                clicks_guardar = []
                for click in ultimosclicks:
                    if click == self.agent.ult_click:
                        break
                    else:
                        clicks_guardar.append(click)
                for click in clicks_guardar:
                    indice = int(click.user.id) - 1
                    articulo = click.article
                    if not articulo in self.agent.tabla_interes[indice]['articulos']: 
                        self.agent.tabla_interes[indice]['articulos'][articulo] = 1
                    else:
                        self.agent.tabla_interes[indice]['articulos'][articulo] += 1
                self.agent.ult_click = uc

            ##
            ## SI HAY COMPRAS NUEVAS
            ##

            if self.agent.ult_compra != uo: ##Funciona similar a los dos casos anteriores.
                print("Nueva(s) compra(s) detectada(s). A trabajar.")
                ultimascompras = Bill.objects.all().order_by('-id')
                compras_guardar = []
                for compra in ultimascompras:
                    if compra == self.agent.ult_compra:
                        break
                    else:
                        compras_guardar.append(compra)
                for compra in compras_guardar:
                    indice = int(compra.user.id) - 1
                    detalles = BillDetails.objects.filter(bill=compra)
                    for detalle in detalles: ##Itero sobre todos los detalles de factura.
                        if detalle.article in self.agent.tabla_interes[indice]['articulos']:
                            self.agent.tabla_interes[indice]['articulos'][detalle.article] -= 15 ##Disminuyo su interés en 15 (Penalización por compra)
                self.agent.ult_compra = uo
                time.sleep(5)

    ## 2) Comportamiento que recomienda productos.
    ## Este comportamiento NO es un behaviour, dado que el sensor realmente es una señal
    ## emitida por Django. Al iniciar sesión por primera vez en un día, se ejecuta.
    ## También se ejecuta cada vez que el usuario da click al botón IA.

    def loginprimeravez(self, user):
        carrito = ShoppingCart.objects.filter(user=user,sponsored=True).delete() ##Borro los carritos patrocinados del pasado.
        categorias = self.tabla_interes[int(user.id)-1]['categorias'] ##Obtengo las categorías de interés del usuario.
        articulos = self.tabla_interes[int(user.id)-1]['articulos'] ##Obtengo los artículos de interés del usuario.
        categorias_max_interes = [] ##Debemos guardar las categorías de mayor interés del usuario.
        articulos_max_interes = [] ##Ídem, con los artículos
        for categoria in categorias:
            if categorias[categoria] >= 10: ##El número 10 para denotar interés es enteramente arbitrario.
                categorias_max_interes.append((categoria, categorias[categoria])) ##Añado a la lista.
        for articulo in articulos:
            if articulos[articulo] >= 5: ##Misma idea, el número 5 es estrictamente arbitrario.
                articulos_max_interes.append((articulo, articulos[articulo])) ##Añado a la lista.
        dos_cat_max_int = [] ##Necesito (máximo) dos categorías de máximo interés.
        dos_art_max_int = [] ##Necesito (máximo) dos artículos de máximo interés.

        ##SOBRE LAS CATEGORIAS:

        if len(categorias_max_interes) <= 2: ##Si tengo 2 categorías o menos, listo.
            for categoria in categorias_max_interes:
                dos_cat_max_int.append(categoria[0]) ##Las añado como sea.
        else: ##De lo contrario, necesito el mayor y el segundo mayor.
            cats = [] ##Las categorías.
            ints = [] ##Sus intereses.
            for categoria in categorias_max_interes: ##Pueblo las listas de categorías e intereses.
                cats.append(categoria[0])
                ints.append(categoria[1])
            indice = ints.index(max(ints)) ##El índice del mayor interés.
            dos_cat_max_int.append(cats[indice]) ##Es también el índice de la categoría.
            cats.pop(indice) ##Remuevo la categoría.
            ints.pop(indice) ##Remuevo su interés. (Para hallar el segundo mayor)
            indice = ints.index(max(ints)) ##Repito el procedimiento para el segundo mayor.
            dos_cat_max_int.append(cats[indice]) ##Listo.
        
        ##SOBRE LOS ARTICULOS:

        if len(articulos_max_interes) <= 2:
            for articulo in articulos_max_interes:
                dos_art_max_int.append(articulo[0])
        else:
            arts = [] ##Los artículos.
            ints = [] ##Sus intereses.
            for artiulo in articulos_max_interes: ##Pueblo las listas de artículos e intereses.
                arts.append(artiulo[0])
                ints.append(artiulo[1])
            indice = ints.index(max(ints)) ##El índice del mayor interés.
            dos_art_max_int.append(arts[indice]) ##Es también el índice del artículo.
            arts.pop(indice) ##Remuevo el artículo.
            ints.pop(indice) ##Remuevo su interés. (Para hallar el segundo mayor)
            indice = ints.index(max(ints)) ##Repito el procedimiento para el segundo mayor.
            dos_art_max_int.append(arts[indice]) ##Listo.     

        ##CREO LOS ARTICULOS:

        carrito_actual = ShoppingCart.objects.filter(user=user) ##Para ingresar en los artículos, debo cuidar el carrito.
        articulos_actuales = [] ##Para eso, guardo los ítems del carrito en una lista.

        for articulo in carrito_actual: 
            articulos_actuales.append(articulo.article)

        for articulo in dos_art_max_int: ##Monto en el carrito de compras todos los artículos.
            if articulo in articulos_actuales:
                pass
            else:
                nvo_carrito = ShoppingCart()
                nvo_carrito.user = user
                nvo_carrito.article = articulo
                nvo_carrito.quantity = 1
                nvo_carrito.amount = articulo.price
                nvo_carrito.sponsored = True
                nvo_carrito.status = 'a'
                nvo_carrito.save() ##Creación del artículo en el carrito normal.
                articulos_actuales.append(articulo)

        ##Caso de las categorías.

        articulos_ingresar_categoria = [] ##En este caso, voy a crear una lista con los artículos que ingresaré.

        for categoria in dos_cat_max_int: ##Esto no es tan sencillo como sólo elegir un ítem de la categoría al azar.
            articulos_categoria = Article.objects.all() ##Como un artículo puede tener muchas categorías...
            articulos_posibles = [] ##debo determinar los artículos que puedo tomar en consideración.
            for articulo in articulos_categoria:
                categorias = articulo.categories.all() ##Extraigo las categorías de cada artículo.
                if categoria in categorias:
                    articulos_posibles.append(articulo) ##Añado el artículo en el listado de los posibles.
            articulos_elegir = [] ##Creo la lista de los artículos que puedo elegir,
            articulos_interes = [] ##y sus respectivos intereses.
            for articulo in articulos_posibles: 
                if articulo in articulos and articulos[articulo] > 2.5 and articulo not in articulos_actuales:
                    ##Esta triple condición es la que elige, a grandes rasgos.
                    ##Primero, el usuario debe haber mostrado interés en el artículo.
                    ##Luego, este interés no puede ser negativo (p. ej - ya lo compré)
                    ##Y este artículo no puede estar en el carrito de compras actualmente.
                    articulos_elegir.append(articulo) ##Lo añado a los posibles artículos.
                    articulos_interes.append(articulos[articulo]) ##Guardo su interés.
            if articulos_elegir: ##Y si existen artículos que cumplan estas características...
                indice = articulos_interes.index(max(articulos_interes)) ##los cargo.
                articulos_ingresar_categoria.append(articulos_elegir[indice]) 
        
        for articulo in articulos_ingresar_categoria: ##Finalmente, monto estos artículos en la BD.
            if articulo in articulos_actuales:
                pass
            else:
                nvo_carrito = ShoppingCart()
                nvo_carrito.user = user
                nvo_carrito.article = articulo
                nvo_carrito.quantity = 1
                nvo_carrito.amount = articulo.price
                nvo_carrito.sponsored = True
                nvo_carrito.status = 'a'
                nvo_carrito.save()      

    ##
    ##3) GENERA CATEGORÍA "RECOMENDADOS"
    ##De los artículos en los que el usuario ha mostrado interés, elige aleatoriamente
    ##4 de ellos y los muestra en el dashboard.

    def categoria_recomendados(self, user): 
        indice = int(user.id)-1 ##Obtengo el índice del usuario.
        interes_usuario = self.tabla_interes[indice] ##Y su tabla de interés.
        articulos_interes = [] ##Monto una lista con los artículos en los que el usuario ha mostrado interés...
        for articulo in interes_usuario['articulos']: 
            if interes_usuario['articulos'][articulo] > 1: ##Interés mayor a 1. Número arbitrario.
                articulos_interes.append(articulo)
        if len(articulos_interes)<=4: ##Si son menos de 4 artículos en total, los recomiendo todos
            DashboardViews.recomendados = articulos_interes
        else: ##En caso contrario, elijo al azar 4 artículos.
            DashboardViews.recomendados = random.sample(articulos_interes, k=4)

    def nuevo_usuario(self, user):
        categorias = dict()
        for categoria in CategoryArticle.objects.all(): ##Carga el diccionario con las categorías,
            categorias[categoria] = 0 ##en interés 0.         
        interes_usuario = { ##Ahora, construyo su elemento para el interes
            'usuario': user.id,
            'ult_conexion': user.last_login,
            'categorias': categorias,
            'articulos': dict()
        }
        self.tabla_interes.append(interes_usuario)

    ##Método que configura el agente.
           
    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.MonitorBusquedasClicks()
        self.add_behaviour(self.b)

##Instanciación del agente.

agente = AgenteGualmar("gualmar@404.city","123456")

def ArrancarAgentes():   
    agente.start()

##Sensores.
##Acá van los métodos sensores, que reciben las señales que emite Django
##e instan al agente a realizar la acción acorde a cada señal. 

@receiver(user_logged_in) ##Cuando el usuario inicia sesión,
def user_logged_in_callback(sender, request, user, **kwargs):    
    if (user.last_login.date()-user.last_access.date()).days != 0: ##si tiene más de un día sin entrar
        agente.loginprimeravez(user) ##le recomienda artículos.
        
@receiver(recomiendame) ##Cuando el usuario solicita que le recomienden artículos,
def recomendar_usuario(user, **kwargs): 
    agente.loginprimeravez(user) ##es el mismo procedimiento que en loginprimeravez.

@receiver(dashboard) ##Cuando el usuario abre el dashboard,
def categoria_recomendados(user, **kwargs):
    agente.categoria_recomendados(user) ##se generan sus recomendaciones aleatorias personalizadas.

@receiver(post_save, sender=User)
def nuevo_usuario(sender, **kwargs):
    user = kwargs.get('instance')
    agente.nuevo_usuario(user)