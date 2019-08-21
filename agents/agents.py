import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

class AgentePrueba(Agent):
    articulos = []
    counter = 0

    class RecibirMensaje(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                self.agent.articulos.append(msg.metadata)

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b2 = self.RecibirMensaje()
        self.add_behaviour(self.b2)

class AgenteEnvia(Agent):
    class EnviarMensaje(OneShotBehaviour):
        async def run(self):
            msg = Message(to="receiver_agent@404.city")
            msg.body = "Hola. Soy un mensajito!"
            await self.send(msg)

            productos = [{
                "codigo":"0000",
                "nombre":"Franela de Caballero",
                "tiempo_busqueda":15,    
            }, {
                "codigo":"0001",
                "nombre":"Laptop VIT i3",
                "tiempo_busqueda":4,
            }, {
                "codigo":"0002",
                "nombre":"Lentejas CASA",
                "tiempo_busqueda":65,
            }]

            for producto in productos:
                msg = Template(to="dummy_agent@404.city")
                msg.body = "nva_busqueda"  
                msg.metadata = producto
                await self.send(msg)
                time.sleep(1)

            self.kill()

    class ImprimirVaina(OneShotBehaviour):
        async def run(self):
            print("Hola! Lo hicimos!")
            self.kill()

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.EnviarMensaje()
        self.add_behaviour(self.b)

    def añadirImpresion(self):
        self.b2 = self.ImprimirVaina()
        self.add_behaviour(self.b2)

class AgenteRecibe(Agent):
    class RecibirMensaje(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("{} dice: Recibí un mensaje con el contenido: '{}'".format(self.agent.jid,msg.body))
            else:
                print("No he recibido mensajes en los últimos 10 segundos.")
            self.kill

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.RecibirMensaje()
        self.add_behaviour(self.b)

enviador = AgenteEnvia("listener_agent@404.city","123456")
receptor = AgenteRecibe("receiver_agent@404.city","123456")
dummy = AgentePrueba("dummy_agent@404.city", "123456")

dummy.start()
time.sleep(2)
receptor.start()
time.sleep(2)
enviador.start()
time.sleep(2)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        for articulo in dummy.articulos:
            print("Codigo del Articulo: {}\nNombre del Articulo: {}\nTiempo de Búsqueda: {}\n".format(articulo["codigo"],articulo["nombre"],articulo["tiempo_busqueda"]))
        break

enviador.añadirImpresion()