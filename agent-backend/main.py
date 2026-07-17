import asyncio
import os
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from report_agent.agent import report_agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry import trace

load_dotenv()

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

if __name__ == "__main__":
    resultado = asyncio.run(run("Mensagem de teste"))
    print(resultado)



