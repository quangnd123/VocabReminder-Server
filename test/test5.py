import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "moonshotai/moonlight-16b-a3b-instruct:free",
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    
  })
)
response = response.json()
print (response)
print(response["usage"]["prompt_tokens"])
print(response["usage"]["completion_tokens"])