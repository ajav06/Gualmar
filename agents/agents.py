import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from core.models import Search, User

class AgenteGualmar(Agent): ##El Agente
    ult_busqueda = Search.objects.all().order_by('-id')[0] ##Guarda la última búsqueda
    ## al momento de iniciar el servidor
    tabla_interes = [] ##Instancia una tabla de interés, vacía, que luego llenará con datos de cada usuario

    class ConstruirTablaInteresPorUsuario(OneShotBehaviour): ##Comportamiento que construye la tabla
        async def run(self):
            for usuario in User.objects.all(): ##Por cada usuario, realiza lo siguiente:
                keywords = dict() ##Crea un diccionario que guardará sus keywords
                busquedas = Search.objects.filter(user_id=usuario.id) ##1) Obtiene todas sus búsquedas,
                for busqueda in busquedas: ##2) Iterando sobre todas sus búsquedas,
                    palabras = busqueda.phrase.split() ##consigo las frases, las divido en palabras.
                    for palabra in palabras: ##3) Por cada palabra,
                        if not keywords[palabra]: ##Si la palabra no existe en los keywords, la añado
                            keywords[palabra] = 1
                        else: ##Si la palabra existe en los keywords, le incremento su interés.
                            keywords[palabra] += 1
                ##Con esto basta para tener todas las keywords que ha buscado un usuario.
                interes_usuario = { ##Ahora, construyo su elemento para el interes
                    'usuario':usuario.id,
                    'ult_conexion':usuario.last_login,
                    'keywords':[
                        keywords
                    ]
                }
                self.tabla_interes.append(interes_usuario) ##Añado a la tabla de interés.
            print(self.tabla_interes)

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.EnviarMensaje()
        self.add_behaviour(self.b)

def ArrancarAgentes():   
    agente = AgenteGualmar("listener_agent@404.city","123456")
    agente.start()