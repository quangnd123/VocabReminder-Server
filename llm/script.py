import pprint 
import httpx
import json 
import os 


async def fetch_openrouter_models(api_key: str = None):
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://openrouter.ai/api/v1/models", headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            response = response.json()
            models = response["data"]
            free_models = []
            for model in models:
                if model["pricing"]["prompt"] == "0" and model["pricing"]["completion"] == "0":
                    free_models.append(model)
            filename = "free_llm.json"
            script_directory = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_directory, filename)
            with open(filepath, 'w') as f:
                json.dump(free_models, f)

        except httpx.HTTPError as e:
            print(f"HTTP error fetching models: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

import asyncio

asyncio.run(fetch_openrouter_models())