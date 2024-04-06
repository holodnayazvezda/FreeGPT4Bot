TOKENS = [
    "6816770761:AAEsxsg7AYylt5PnSBE-xD7GEsax0tfy0Ko",
    "6516286815:AAEmfpvL-495eOO3dMppRKf_PEil5SrcXrQ",
    "6748141136:AAEIjr4dgrXNd1UJdBeeyaKCPjO0EDHhQ6c",
    "6790464369:AAFnIeVpE2IMRPGVkP5m1tU8V5ZMePQ0Lrk",
    "7162028483:AAGQDQqsNdouuClMpw1BB_L1s4OD54o6av8"
]

TEST_TOKENS = [
    "7188875369:AAGXnUceM26kXD66D-0bqe6kVqd9XenL8oQ"
]

ADMINS = [1071845329, 1925785299]

GIGACHAT_CLIENT_SECRET = "YjViZGI1NzctMDBlYi00YTZjLThhOTYtOTUzODQ5MGE0ZGRjOmMzNDlmNzdjLTEwMzMtNDFiYS04ZTY4LWZhNTE2MGEzYzE0MQ=="

REDIS_URL = 'redis://localhost:6379'

OCR_SPACE_API_KEYS = ['K85720388688957', 'K89292650388957', 'K89083415488957', 'K84384523188957', 'K89142091988957',
                      'K87164054488957', 'K84054502088957', 'K82657306788957', 'K83028254688957', 'K81585714888957',
                      'K84731190188957', 'K84676433588957', 'K89859164888957', 'K87616973288957', 'K83094111388957']
amount_of_requests_to_ocr_api = 0

LENGTH_OF_GPT3_HISTORY_FOR_USERS = 5
LENGTH_OF_GPT4_HISTORY_FOR_USERS = 8
COOKIES_FOR_GPT_4_BING_USERS = {"set-cookie": "MUIDB=372BDD60E86A691C124CC95BE9C068E1; expires=Tue, 01-Apr-2025 21:21:26 GMT; path=/; HttpOnly", "useragentreductionoptout": "A7kgTC5xdZ2WIVGZEfb1hUoNuvjzOZX3VIV/BA6C18kQOOF50Q0D3oWoAm49k3BQImkujKILc7JmPysWk3CSjwUAAACMeyJvcmlnaW4iOiJodHRwczovL3d3dy5iaW5nLmNvbTo0NDMiLCJmZWF0dXJlIjoiU2VuZEZ1bGxVc2VyQWdlbnRBZnRlclJlZHVjdGlvbiIsImV4cGlyeSI6MTY4NDg4NjM5OSwiaXNTdWJkb21haW4iOnRydWUsImlzVGhpcmRQYXJ0eSI6dHJ1ZX0="}

MODELS_DATA = {
    '🔁 Переключиться на gpt-3.5-turbo': {
        'name': 'gpt-3.5-turbo',
        'quantity_of_req_table_name': 'quantity_of_requests_to_gpt3'
    },
    '🔁 Переключиться на gpt-4-turbo': {
        'name': 'gpt-4-turbo',
        'quantity_of_req_table_name': 'quantity_of_requests_to_gpt4_turbo'
    },
    '🔁 Переключиться на GigaChat': {
        'name': 'GigaChat',
        'quantity_of_req_table_name': 'quantity_of_requests_to_gigachat'
    }
}
SELECT_MODEL_BUTTONS = list(MODELS_DATA.keys())
AVAILABLE_REACTIONS = ['❤️', '🤔', '👌', '🤝', '🫡', '✍️']
