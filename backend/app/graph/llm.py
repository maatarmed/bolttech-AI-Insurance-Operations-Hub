from langchain_core.language_models.chat_models import BaseChatModel

from app.config import get_settings


def get_chat_model() -> BaseChatModel | None:
    settings = get_settings()
    if settings.llm_provider == "bedrock":
        try:
            from langchain_aws import ChatBedrock

            return ChatBedrock(
                model_id=settings.bedrock_model_id,
                region_name=settings.aws_region,
                model_kwargs={"temperature": 0},
            )
        except Exception:
            return None
    if not settings.openai_api_key:
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
        temperature=0,
    )
