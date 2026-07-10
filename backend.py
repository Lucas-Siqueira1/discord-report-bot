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