from openai import OpenAI
from dotenv import load_dotenv
import os
from agent import Agent

load_dotenv()
print("Mi primer agente de IA")

client = OpenAI()
agent = Agent()

while True:
    user_input = input("Tú: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("exit", "bye", "fin"):
        print("\n¡Hasta luego!\n")
        break

    # Agregamos el mensaje del usuario al historial
    agent.messages.append({"role": "user", "content": user_input})

    # Solo hacemos una llamada al modelo por cada input del usuario
    response = client.responses.create(
        model="gpt-5-nano",
        input=agent.messages,
        tools=agent.tools
    )
    # Llamar una sola vez más si el modelo invocó una herramienta
    called_tool = agent.process_response(response)
    if called_tool:
        response = client.responses.create(
            model="gpt-5-nano",
            input=agent.messages,
            tools=agent.tools
        )
        agent.process_response(response)
