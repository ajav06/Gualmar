import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from core.models import Search, User, Article, CategoryArticle
import collections
from datetime import datetime

class AgenteGualmar(Agent): ##El Agente
    ult_busqueda = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda
    ## al momento de iniciar el servidor
    tabla_interes = [] ##Instancia una tabla de interés, vacía, que luego llenará con datos de cada usuario

    class ConstruirTablaInteresPorUsuario(OneShotBehaviour): ##Comportamiento que construye la tabla
        async def run(self):
            for usuario in User.objects.all(): ##Por cada usuario, realiza lo siguiente:
                keywords = dict() ##Crea un diccionario que guardará sus keywords
                categorias = dict() ##Crea un diccionario que guardará las categorías.
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
                                cx = articulo.categories.all() ##obtengo sus categorías,
                                for cat in cx: ##y por cada categoría del artículo,
                                    if not cat in categorias_añadidas: ##si no la he añadido ya, incremento su interés
                                        categorias[cat] += 0.5 / (int((datetime.now().date()-busqueda.time).days) + 1)
                                        categorias_añadidas.append(cat) ##Para hacerlo una sola vez por cada categoría que resulte de la búsqueda (p. ej "laptop" no suma tantas veces como computadores en tecnología, sino una sola vez)
                            if not palabra in keywords: ##Si la palabra no existe en los keywords, la añado
                                keywords[palabra] = 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Incremento su interés.
                            else: ##Si la palabra existe en los keywords, le incremento su interés.
                                keywords[palabra] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1)
                        categorias[categoria] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Incremento el interés de la categoría por haber sido buscada.
                    elif categoria: ##Si la búsqueda tuvo sólo la categoría.
                        categorias[categoria] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Lo único que hago es incrementar el interés de la categoría por haber sido buscada.
                    elif palabras: ##Si la búsqueda tuvo sólo la palabra.
                        palabras = str(busqueda.phrase).split() ##consigo las frases, las divido en palabras.
                        for palabra in palabras: ##Por cada palabra,
                            categorias_añadidas = [] ##voy a guardar las categorías de estos objetos que ya he contado.
                            for articulo in (Article.objects.filter(name__contains=palabra) | Article.objects.filter(description__contains=palabra)).distinct(): ##Sobre los artículos que resultan de buscar esta palabra,
                                cx = articulo.categories.all() ##obtengo sus categorías,
                                for cat in cx: ##y por cada categoría del artículo,
                                    if not cat in categorias_añadidas: ##si no la he añadido ya, incremento su interés
                                        categorias[cat] += 0.5 / (int((datetime.now().date()-busqueda.time).days) + 1)
                                        categorias_añadidas.append(cat) ##Para hacerlo una sola vez por cada categoría que resulte de la búsqueda (p. ej "laptop" no suma tantas veces como computadores en tecnología, sino una sola vez)
                            if not palabra in keywords: ##Si la palabra no existe en los keywords, la añado
                                keywords[palabra] = 1 / (int((datetime.now().date()-busqueda.time).days) + 1) ##Incremento su interés.
                            else: ##Si la palabra existe en los keywords, le incremento su interés.
                                keywords[palabra] += 1 / (int((datetime.now().date()-busqueda.time).days) + 1)
                ##Con esto basta para tener todas las keywords y categorías por las que un usuario ha mostrado interés.
                for preferencia in usuario.preferences.all(): ##Me faltan sus preferencias,
                    categorias[preferencia] += 5 ##tienen un peso mayor.
                interes_usuario = { ##Ahora, construyo su elemento para el interes
                    'usuario':usuario.id,
                    'ult_conexion':usuario.last_login,
                    'keywords':[
                        keywords
                    ],
                    'categorias':[
                        categorias
                    ]
                }
                self.agent.tabla_interes.append(interes_usuario) ##Añado a la tabla de interés.
            print(self.agent.tabla_interes)

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.ConstruirTablaInteresPorUsuario()
        self.add_behaviour(self.b)

def ArrancarAgentes():   
    agente = AgenteGualmar("listener_agent@404.city","123456")
    agente.start()