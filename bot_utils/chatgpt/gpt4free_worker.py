import g4f
import asyncio
import tiktoken
from threading import Thread

from bot_utils.async_process_runner import async_functions_process_starter
from bot_utils.chatgpt.chat_gpt_users_worker import *
from bot_utils.chatgpt.chat_gpt_worker import ask_chat_gpt_and_return_answer
from bot_utils.chatgpt.requests_counter import *


async def ask_chat_gpt_temporary_api(prompt: str, user_id: int) -> str:
    history_of_requests = await get_history_of_requests("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3",
                                                        "users_history", user_id, "gpt-3.5-turbo")
    history_of_requests.append({'role': 'user', 'content': prompt})
    response_content = await g4f.ChatCompletion.create_async(
        model="gpt-4",
        messages=history_of_requests,
    )
    await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                 user_id, prompt, 'user')
    await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                 user_id, response_content, 'assistant')
    return response_content


async def ask_chat_gpt_4(prompt: str, user_id: int) -> tuple:
    tokens_in_response = len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(prompt)) + 7
    history_of_requests = await get_history_of_requests("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3",
                                                        "users_history", user_id, "gpt-4")
    history_of_requests.append({'role': 'user', 'content': prompt})
    if tokens_in_response > 4096:
        return None, 400
    try:
        response_content = await g4f.ChatCompletion.create_async(
            model="gpt-4-turbo",
            messages=history_of_requests
        )
        await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                     user_id, prompt, 'user')
        await add_request_to_history("./bot_data/databases/history_of_requests_to_chatgpt.sqlite3", "users_history",
                                     user_id, response_content, 'assistant')
        Thread(target=async_functions_process_starter, args=(increase_the_number_of_requests_for_the_user,
                                   ["./bot_data/databases/quantity_of_requests.sqlite3",
                                    'quantity_of_requests_to_gpt4_turbo', user_id])).start()
        return response_content.replace('Bing', 'ReshenijaBotGpt'), 200
    except Exception as e:
        print(e)
        response_content, status_code = await ask_chat_gpt_and_return_answer('gpt-3.5-turbo', prompt, user_id)
        if status_code == 200:
            return response_content, status_code
        else:
            return None, status_code


async def main() -> None:
    response_content, status_code = await ask_chat_gpt_4("привет", 800)
    print(response_content, status_code)
            

if __name__ == '__main__':
    asyncio.run(main())
