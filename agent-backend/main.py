import os
import uuid
from typing import List
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langfuse import get_client
from evaluation import quality_eval
from google.adk.runners import Runner
from report_agent.agent import report_agent
from google.genai.types import Content, Part
from google.adk.sessions import InMemorySessionService
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

load_dotenv()

app = FastAPI()
langfuse = get_client()

try:
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")
except Exception as e:
    print(f"Langfuse auth check skipped: {e}")

if os.getenv("ENABLE_ADK_TRACING") == "1":
    GoogleADKInstrumentor().instrument()

session_service = InMemorySessionService()
runner = Runner(
    agent=report_agent,
    app_name="report_bot",
    session_service=session_service
)

async def run(mensagens: str) -> str:
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(
        app_name="report_bot",
        user_id="job_report",
        session_id=session_id
    )   

    conteudo = Content(parts=[Part(text=mensagens)])

    resposta_final = ""
    trace_id = None

    async for event in runner.run_async(user_id="job_report", session_id=session_id, new_message=conteudo):
                
        if event.is_final_response():
            resposta_final = event.content.parts[0].text
    
    try:
        langfuse.flush()
    except Exception as e:
        print(f"Langfuse flush skipped: {e}")

    
    return resposta_final

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




