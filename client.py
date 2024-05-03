from groq import Groq
from aiohttp import web
from settings import GROQ_API_KEY, GROQ_DEFAULT_MODEL

from util import read_file

# System Message
system_message = read_file("role/system.txt")

# Creates text based on preceding and following text
def create_text(prompt):
  try:
    completion = Groq(
      api_key=GROQ_API_KEY,
    ).chat.completions.create(
    model=GROQ_DEFAULT_MODEL,
    messages=[
    {
      "role": "system",
      "content": system_message
    },
    {
      "role": "user",
      "content": prompt
    }
    ])
  except Exception as e:
    print(e)
    raise web.HTTPInternalServerError()
  return completion.choices[0].message.content