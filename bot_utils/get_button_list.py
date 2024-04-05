from bot_data.config import SELECT_MODEL_BUTTONS


async def get_button_list_for_selected_model(model: str) -> list[str]:
    return list(filter(lambda btn_text: model not in btn_text, SELECT_MODEL_BUTTONS))
