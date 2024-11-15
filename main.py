import json

import httpx
import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import AsyncClient
from openai.pagination import AsyncPage
from openai.types import Model
from openai.types.chat import ChatCompletion
from openai.types.chat.completion_create_params import CompletionCreateParams
from starlette.responses import StreamingResponse

from settings import settings
from utils import iter_async_stream, NON_STREAM_MODELS, handle_non_stream_models

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
        message = json.dumps(e.body) if e.body else e.message
        status_code = e.status_code if hasattr(e, "status_code") else 400
        print(status_code, type(e).__name__, message)
        return JSONResponse(
            content=message,
            status_code=status_code,
        )


@app.post("/v1/chat/completions", response_model=ChatCompletion)
async def chat_completions(params: CompletionCreateParams):
    stream_support = params['model'] not in NON_STREAM_MODELS
    stream_requested = params.get('stream', False)
    params['stream'] = stream_requested and stream_support
    response = await client.chat.completions.create(**params)
    if stream_requested:
        if stream_support:
            stream = iter_async_stream(response)
        else:
            stream = handle_non_stream_models(response)
        return StreamingResponse(
            content=stream,
            media_type="text/event-stream; charset=utf-8",
        )
    return response


@app.get("/v1/models")
async def models() -> AsyncPage[Model]:
    return await client.models.list()
