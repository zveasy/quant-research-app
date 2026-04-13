from openai import OpenAI

from app.config import settings


class OpenAIResponsesClient:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)

    def create_research_response(self, user_request: str, tools: list[dict]) -> dict:
        response = self._client.responses.create(
            model=settings.openai_model_main,
            input=user_request,
            tools=tools,
        )
        return response.model_dump()
