import requests, os
from dotenv import load_dotenv
load_dotenv()

r = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': 'Bearer ' + os.getenv('OPENROUTER_API_KEY'),
        'Content-Type': 'application/json'
    },
    json={
        'model': 'mistralai/mistral-7b-instruct',
        'messages': [{'role': 'user', 'content': 'hello'}]
    }
)
print(r.json())