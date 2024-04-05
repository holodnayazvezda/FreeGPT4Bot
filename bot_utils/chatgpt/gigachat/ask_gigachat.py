from threading import Thread

from bot_data.config import GIGACHAT_CLIENT_SECRET
from bot_utils.async_process_runner import async_functions_process_starter
from bot_utils.chatgpt.chat_gpt_users_worker import get_history_of_requests, add_request_to_history
from bot_utils.chatgpt.chat_gpt_worker import ask_chat_gpt_and_return_answer
from bot_utils.chatgpt.gigachat.gigachat_image_worker import get_images_from_gigachats_answer
from bot_utils.chatgpt.gigachat.tokens_calculator import calculate_prompt_tokens

from langchain.chat_models.gigachat import GigaChat

from bot_utils.chatgpt.requests_counter import increase_the_number_of_requests_for_the_user


async def ask_gigachat(prompt: str, user_id: int) -> tuple:
    tokens_in_request = calculate_prompt_tokens(prompt)
    if tokens_in_request > 1024:
        return None, 400
    history_of_requests = await get_history_of_requests("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3",
                                                        "users_history", user_id, "GigaChat")
    history_of_requests.append({'role': 'user', 'content': prompt})
    try:
        gigachat = GigaChat(
            credentials=GIGACHAT_CLIENT_SECRET,
            verify_ssl_certs=False
        )
        response = await gigachat.ainvoke(history_of_requests)
        response_content = response.content
        images_in_response = await get_images_from_gigachats_answer(response_content)
        if images_in_response[0]:
            return images_in_response[1], 808
        await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                     user_id, prompt, 'user')
        await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                     user_id, response_content, 'assistant')
        Thread(target=async_functions_process_starter,
               args=(increase_the_number_of_requests_for_the_user, ["./bot_data/databases/quantity_of_requests.sqlite3",
                     'quantity_of_requests_to_gigachat', user_id])).start()
        return response_content, 200, False
    except Exception as e:
        print(e)
        response_content, status_code = await ask_chat_gpt_and_return_answer('gpt-3.5-turbo', prompt, user_id)
        if status_code == 200:
            return response_content, status_code
        else:
            return None, status_code, False
