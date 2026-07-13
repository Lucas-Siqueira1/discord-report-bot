<<<<<<< HEAD
from fastapi import FastAPI
from pydantic import BaseModel, TypeAdapter
from typing import List
from main import run

app = FastAPI()

class Mensagem(BaseModel):
    autor: str
    hora: str
    texto: str

class ListaMensagens(BaseModel):
    mensagens: List[Mensagem]

@app.post("/report")
async def gerar_report(mensagens_obj: ListaMensagens):

    mensagens_str = mensagens_obj.model_dump_json()
    report = await run(mensagens_str)
    return report
=======
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import datetime 
import os

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

utc = datetime.timezone.utc
time = datetime.time(hour=18, tzinfo=utc)

canal = ""
lider = ""

@bot.event
async def on_ready():
    global canal 
    global lider 

    canal = bot.get_channel(1525202052697821335)
    lider = await bot.fetch_user(834030976002031616)

@tasks.loop(time=time)
async def rotina_diaria():

    periodo = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)
    historico_diario = []

    async for message in canal.history(limit=None, after=periodo):
        if not message.author.bot:
            historico_diario.append({
                "usuario":message.author.name,
                "hora": message.created_at.strftime("%H:%M"),
                "texto": message.content
            })
    
    if not historico_diario:
        print("Nenhuma nova mensagem foi enviada hoje")
        return
    
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
        
    if not historico_semanal:
        print("Nenhuma nova mensagem enviada essa semana")
        return
    
bot.run(token)
    
>>>>>>> temp-bot/main
