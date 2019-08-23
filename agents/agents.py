import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from core.models import Search

class AgenteEscucha(Agent):
    ult_busqueda = Search.objects.all().order_by('id')
    print(ult_busqueda)

    async def setup(self):
        print("Comenzando el agente {}".format(str(self.jid)))
        self.b = self.EnviarMensaje()
        self.add_behaviour(self.b)

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