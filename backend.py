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
    
