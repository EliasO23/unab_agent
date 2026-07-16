# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Pregunta del usuario")
    session_id: str | None = Field(default=None, description="Identificador opcional de sesión")


class ChatResponse(BaseModel):
    answer: str
    classification: str
    used_multiquery: bool
    num_fragments: int


class HealthResponse(BaseModel):
    status: str = "ok"
