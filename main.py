from http import HTTPMethod

import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.api_route("/{path:path}", methods=[
    HTTPMethod.CONNECT,
    HTTPMethod.DELETE,
    HTTPMethod.GET,
    HTTPMethod.HEAD,
    HTTPMethod.OPTIONS,
    HTTPMethod.PATCH,
    HTTPMethod.POST,
    HTTPMethod.PUT,
    HTTPMethod.TRACE,
])
async def proxy_openai_requests(request: Request, path: str):
    url = f"https://openai.com/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=request.stream(),
        )
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
    )
