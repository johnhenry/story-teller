from groq import Groq

from settings import GROQ_API_KEY

def createClient(API_KEY=GROQ_API_KEY):
  return Groq(
    api_key=API_KEY,
  )
