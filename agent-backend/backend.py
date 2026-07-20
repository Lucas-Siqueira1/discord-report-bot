from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from main import run
from evaluation import quality_eval

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

    evaluation = quality_eval(input=mensagens_str, output=report)
    print(f"Score de qualidade: {evaluation.value}\n\nComentário: {evaluation.comment}")

    return report