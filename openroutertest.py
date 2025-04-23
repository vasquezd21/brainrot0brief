import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
}

response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
print(response.json())
