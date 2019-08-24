import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from core.models import Search, User, Article, CategoryArticle, ArticleClick, Bill, BillDetails
import collections
from datetime import datetime

class AgenteGualmar(Agent): ##El Agente
    ult_busqueda = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda
    ult_click = ArticleClick.objects.all().order_by('-id')[0] ##Guarda el último click
    ult_compra = Bill.objects.all().order_by('-id')[0] ##Guarda la última factura
    ## al momento de iniciar el servidor
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
                    if palabras and categoria: ##Si la búsqueda tuvo frase y categoría:
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
                        categorias[categoria] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Incremento el interés de la categoría por haber sido buscada.
                    elif categoria: ##Si la búsqueda tuvo sólo la categoría.
                        categorias[categoria] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Lo único que hago es incrementar el interés de la categoría por haber sido buscada.
                    elif palabras: ##Si la búsqueda tuvo sólo la palabra.
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
                            articulosd[detalle.article] -= 15 ##Disminuyo su interés en 15 (Penalización por compra)
                        else:
                            articulosd[detalle.article] = -15 ##Establezco su interés en -15

                interes_usuario = { ##Ahora, construyo su elemento para el interes
                    'usuario': usuario.id,
                    'ult_conexion': usuario.last_login,
                    'categorias': categorias,
                    'articulos': articulosd
                }
                self.agent.tabla_interes.append(interes_usuario) ##Añado a la tabla de interés.
            print(self.agent.tabla_interes)
        
        async def run(self): ##Voy a observar las nuevas búsquedas y/o clicks.
            ub = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda (actual)
            uc = ArticleClick.objects.all().order_by('-id')[0] ##Guarda el último click (actual)
            uo = Bill.objects.all().order_by('-id')[0] ##Guarda la última compra.

            ##
            ## SI HAY BUSQUEDAS NUEVAS
            ##

            if self.agent.ult_busqueda != ub:
                print("Nueva(s) búsqueda(s) detectada(s). A trabajar.")
                ultimasbusquedas = Search.objects.all().order_by('-id')
                busquedas_guardar = []
                for busqueda in ultimasbusquedas:
                    if busqueda == self.agent.ult_busqueda:
                        break
                    else:
                        busquedas_guardar.append(busqueda)
                for busqueda in busquedas_guardar:
                    indice = int(busqueda.user.id)-1
                    frase = busqueda.phrase
                    categoria = busqueda.category
                    if frase:
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
                    if categoria:
                        self.agent.tabla_interes[indice]['categorias'][categoria] += 1
                print(self.agent.tabla_interes[indice])
                self.agent.ult_busqueda = ub
            
            ##
            ## SI HAY CLICKS NUEVOS
            ##

            if self.agent.ult_click != uc:
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
                print(self.agent.tabla_interes[indice])
                self.agent.ult_click = uc

            ##
            ## SI HAY COMPRAS NUEVAS
            ##
            if self.agent.ult_compra != uo:
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
                time.sleep(5)

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.MonitorBusquedasClicks()
        self.add_behaviour(self.b)

def ArrancarAgentes():   
    agente = AgenteGualmar("listener_agent@404.city","123456")
    agente.start()