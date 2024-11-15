from collections.abc import AsyncGenerator

from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk, chat_completion_chunk

NON_STREAM_MODELS = {
    "o1-preview",
    "o1-mini",
}


async def iter_async_stream(stream: AsyncStream) -> AsyncGenerator[str, None]:
    async for chunk in stream:
        yield f"data: {chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


def handle_non_stream_models(completion: ChatCompletion) -> AsyncGenerator[str, None]:
    choice = completion.choices[0]
    original_content = choice.message.content
    for content in ["", original_content, None]:
        chunk = ChatCompletionChunk(
            **completion.model_dump(exclude={"choices", "object"}),
            object="chat.completion.chunk",
            choices=[
                chat_completion_chunk.Choice(
                    **choice.model_dump(exclude={"message"}),
                    delta=chat_completion_chunk.ChoiceDelta(
                        **choice.message.model_dump(exclude={"audio", "content"}),
                        content=content,
                    )
                )
            ]
        )
        yield f"data: {chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"
