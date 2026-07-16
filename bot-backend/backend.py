import os
import discord
import datetime 
import requests
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from discord.ext import commands, tasks

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

fuso_brasil = datetime.timezone(datetime.timedelta(hours=-3))
time = datetime.time(hour=18, tzinfo=fuso_brasil)

canal = ""
lider = ""

url = "http://agent-backend:8000/report"

@bot.event
async def on_ready():
    global canal 
    global lider 

    canal = bot.get_channel(1525202052697821335)
    lider = await bot.fetch_user(834030976002031616)

    if not rotina_diaria.is_running():
        rotina_diaria.start()
    
    if not rotina_semanal.is_running():
        rotina_semanal.start()




class Mensagem(BaseModel):
    autor: str
    hora: str
    texto: str

class ListaMensagens(BaseModel):
    mensagens: List[Mensagem]

@tasks.loop(time=time)
async def rotina_diaria():

    dia_verificacao = datetime.date.today().weekday()
    if dia_verificacao == 6:
        return

    periodo = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)
    historico_diario = []

    async for message in canal.history(limit=None, after=periodo):
        if not message.author.bot:
            historico_diario.append({
                "autor":message.author.name,
                "hora": message.created_at.strftime("%H:%M"),
                "texto": message.content
            })
    
    historico_formatado = ListaMensagens(mensagens=historico_diario)

    response = requests.post(url, json=historico_formatado.model_dump())
    report_bruto = response.json()
    report_tratado = report_bruto[:2000]


    await lider.send(report_tratado)
    
    
    
@tasks.loop(time=time)
async def rotina_semanal():
    
    dia_verificacao = datetime.date.today().weekday()
    if dia_verificacao != 6:
        return
    
    periodo = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=154)
    historico_semanal = []

    async for message in canal.history(limit=None, after=periodo):
        if not message.author.bot:
            historico_semanal.append({
                "usuario": message.author.name,
                "hora": message.created_at.strftime("%H:%M"),
                "texto": message.content
            })

    historico_formatado = ListaMensagens(mensagens=historico_semanal)

    response = requests.post(url, json=historico_formatado.model_dump())
    report_bruto = response.json()
    report_tratado = report_bruto[:2000]

    await lider.send(report_tratado)
        
   
bot.run(token)
    
