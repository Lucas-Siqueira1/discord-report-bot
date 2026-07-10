import os 
import asyncio
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from report_agent.agent import report_agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

load_dotenv()

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

    async for event in runner.run_async(user_id="job_report", session_id=session_id, new_message=conteudo):
        if event.is_final_response():
            resposta_final = event.content.parts[0].text

    
    return resposta_final

if __name__ == "__main__":
    resultado = asyncio.run(run("Mensagem de teste"))
    print(resultado)



