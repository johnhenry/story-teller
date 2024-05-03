from pathlib import Path
from decouple import config

GROQ_API_KEY = config('GROQ_API_KEY')
GROQ_DEFAULT_MODEL = config('GROQ_DEFAULT_MODEL', default='llama3-8b-8192')
PAGE_MAX = config('PAGE_MAX', default=16, cast=int)
PAGE_REACH = config('PAGE_REACH', default=3, cast=int)
PAGE_PATH = Path(config('PAGE_PATH', default="page"))
SITE_ROOT = Path(config('SITE_ROOT', default="/"))