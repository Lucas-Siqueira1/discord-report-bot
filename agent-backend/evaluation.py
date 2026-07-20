import os
import re
from langfuse.experiment import Evaluation
from openai import OpenAI

def get_client():
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

def quality_eval(*, input, output, **kwargs):
    client = get_client()
    prompt = f"""Você é um avaliador especialista (LLM-as-a-Judge) responsável por analisar a qualidade 
                de relatórios automatizados gerados a partir de conversas de desenvolvedores no Discord.

                Sua tarefa é avaliar o relatório em duas dimensões principais:
                1. Completude (Recall): O relatório capturou todas as atualizações de progresso, decisões técnicas, 
                tarefas e bloqueios relevantes? (Ignore ruídos, saudações e conversas informais).
                2. Fidelidade (Faithfulness): O relatório é fiel às mensagens originais ou inventou/alucinou fatos que não aconteceram?

                ### Escala de Avaliação:
                - 1.0 = Excelente. O relatório resume de forma concisa e relevante todos os pontos técnicos importantes sem omitir nada crítico e sem alucinar.
                - 0.5 = Parcial. O relatório omitiu 1 ou 2 assuntos técnicos relevantes OU incluiu detalhes excessivos e desnecessários.
                - 0.0 = Ruim. O relatório omitiu progressos críticos, distorceu os fatos ou alucinou informações não presentes nas mensagens.

                ### Instruções de Saída:
                1. Primeiro, escreva uma justificativa detalhada comparando as mensagens com o report.
                2. Ao final, atribua a nota numérica exata (0.0, 0.5 ou 1.0).

                Retorne ESTRITAMENTE no seguinte formato:
                JUSTIFICATIVA: <seu raciocínio analítico aqui>
                NOTA: <apenas o número: 0.0, 0.5 ou 1.0>

                ---
                Mensagens do Discord:
                {input}

                Report Gerado:
                {output}
                """
    
    user_messages = f"""Mensagens do discord: {input}
                       Report gerado: {output}"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=600,
        temperature=0.0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_messages}
        ]
    )

    raw = response.choices[0].message.content.strip()
    
    match = re.search(
        r"JUSTIFICATIVA:\s*(.*?)\s*NOTA:\s*(0\.0|0\.5|1\.0)",
        raw,
        re.DOTALL
    )

    if match:
        comentario = match.group(1).strip()
        score = float(match.group(2))
    else:
        comentario = f"Falha no parsing da justificativa. Saída bruta: {raw}"
        score = 0.5

    return Evaluation(name="quality", value=score, comment=comentario)

          