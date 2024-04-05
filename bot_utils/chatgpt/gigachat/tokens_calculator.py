from langchain.chat_models.gigachat import GigaChat
from bot_data.config import GIGACHAT_CLIENT_SECRET


def calculate_prompt_tokens(prompt: str) -> int:
    gigachat = GigaChat(
        credentials=GIGACHAT_CLIENT_SECRET,
        verify_ssl_certs=False
    )
    s = gigachat.tokens_count(input_=[prompt])
    return s[0].tokens
