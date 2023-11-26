import base64
import requests
from io import BytesIO
from PIL import Image
import os

# OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']

def analyze_image(image: Image):
  buffered = BytesIO()
  image.save(buffered, format="JPEG")
  base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What’s in this image?"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  result = response.json()['choices'][0]['message']['content']

  return(result)
