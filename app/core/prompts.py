# -*- coding: utf-8 -*-
"""
Plantillas de prompt usadas por el agente:
1. CLASSIFIER_PROMPT -> LLM de clasificación, corre ANTES del
                         multiquery para evitar gastar tokens si la
                         pregunta no es institucional.
2. MULTIQUERY_PROMPT -> LLM generador de sub-consultas.
3. RESPONSE_PROMPT   -> LLM de respuesta final.

"""

from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# 1. Prompt de clasificación - se ejecuta ANTES del multiquery
# ---------------------------------------------------------------------------
CLASSIFIER_PROMPT = PromptTemplate.from_template(
    """
Eres un clasificador binario para el asistente virtual de la Universidad Doctor
Andrés Bello (UNAB).

Tu única tarea es decidir si la siguiente pregunta de un usuario corresponde a
un tema institucional/universitario (reglamentos, becas, notas, matrícula,
trámites administrativos, procesos académicos, docentes, sanciones,
infraestructura, calendarios, requisitos de graduación, etc.) o si, por el
contrario, es un tema ajeno a la universidad (deportes, política externa,
entretenimiento, salud personal no relacionada a la universidad, cultura
general, u otros temas sin relación con la vida universitaria).

Responde ÚNICAMENTE con una sola palabra, sin explicaciones ni puntuación:
- INSTITUCIONAL  -> si la pregunta corresponde a temas de la universidad.
- FUERA_DE_ALCANCE -> si la pregunta no corresponde a temas de la universidad.

Pregunta del usuario:
{question}

Respuesta (una sola palabra):
"""
)

OUT_OF_SCOPE_MESSAGE = (
    "Esta consulta está fuera del alcance del asistente universitario. Yo estoy "
    "para ayudarte en temas relacionados con reglamentos oficiales, procesos y "
    "documentación institucional de la UNAB.\n\n¿En qué puedo ayudarte?"
)

