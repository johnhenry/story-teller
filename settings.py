import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_DEFAULT_MODEL = os.environ.get("GROQ_DEFAULT_MODEL") or "llama3-8b-8192"
PAGE_MAX = 32
PAGE_REACH = 3