import json

import httpx
import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from openai.types.chat.completion_create_params import CompletionCreateParamsNonStreaming

from settings import settings

app = FastAPI()

client = AsyncClient(
    api_key=settings.openai_api_key.get_secret_value(),
    http_client=httpx.AsyncClient(
        proxy=settings.proxy.get_secret_value(),
    ),
)


@app.middleware("http")
async def handle_openai_api_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except openai.APIError as e:
        return JSONResponse(
            content=json.dumps(e.body) if e.body else e.message,
            status_code=e.status_code if hasattr(e, 'status_code') else 400,
        )


@app.post("/chat/completions")
async def chat_completions(params: CompletionCreateParamsNonStreaming) -> ChatCompletion:
    return await client.chat.completions.create(**params)
