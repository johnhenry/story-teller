from aiohttp import web
from random import randrange
from groq import Groq
from settings import GROQ_DEFAULT_MODEL, PAGE_MAX, PAGE_REACH
from client import createClient

# System Message
# with open('role/system.txt', 'r') as file:
#   system_message = file.read()

# Prompts
with open('prompt/first.txt', 'r') as file:
  prompt_first = file.read()
with open('prompt/mid.txt', 'r') as file:
  prompt_mid = file.read()
with open('prompt/last.txt', 'r') as file:
  prompt_last = file.read()

# Creates text based on preceding and following text
def create_text(text_before, text_after, prompt):
    try:
      completion = createClient().chat.completions.create(
      model=GROQ_DEFAULT_MODEL,
      messages=[
      # {
      #   "role": "system",
      #   "content": system_message
      # },
      {
        "role": "user",
        "content": prompt.format(previous=text_before, next=text_after)
      }
      ])
    except Exception as e:
      print(e)
      raise web.HTTPInternalServerError()
    return completion.choices[0].message.content

# Creates page based preceding and following pages
def create_page(page, reach=PAGE_REACH):
  with open(f"page/{page}.txt", 'w') as file:
    pages_before =[]
    for i in range(reach+1):
      try:
        with open(f"page/{page-i}.txt", "r") as f:
          text= f.read()
          pages_before.insert(0,text)
      except FileNotFoundError:
        break
    pages_after =[]
    for i in range(reach+1):
      try:
        with open(f"page/{page+i}.txt", "r") as f:
          pages_after.append(f.read())
      except FileNotFoundError:
        break
    text_before = "\n".join(pages_before)
    text_after = "\n".join(pages_after)
    if page == 0:
      prompt = prompt_first
    elif page == PAGE_MAX - 1:
      prompt = prompt_last
    else:
      prompt = prompt_mid
    text = create_text(text_before, text_after, prompt)
    file.write(text)
  return text, text_before.replace("\n", ""), text_after.replace("\n", "")

# Route Handler: Sends user to a random page
def handleRandom(_):
  raise web.HTTPFound(f"/{randrange(PAGE_MAX)}")

# Wrap stext in HTML
def wrapHTML(text, index):
  numbered_links = []
  for i in range(PAGE_MAX):
    numbered_links.append(f"<a href=\"/{i}\">{i}</a>")
  numbered_links = "".join(numbered_links)
  return f"""
  <html>
  <head>
    <title>Story</title>
    <style>

      nav {{
        width: 100%;
        display: flex;
        justify-content: flex-start;
        gap: 1rem;
        flex-wrap: wrap;
      }}
      pre {{
        word-wrap: break-word;
        white-space: pre-wrap;
      }}
    </style>
  </head>
  <body>
    <h1 title="current">{index}</h1>
    <nav>
      <a title="start" href="/0">&lt;&lt;</a>
      <a title="previous" href="/{index-1}">&lt;</a>
      <a title="random" href="/">🎲</a>
      <a title="next" href="/{index+1}">&gt;</a>
      <a title="end" href="/{PAGE_MAX-1}">&gt;&gt;</a>
    </nav>
    <pre>{text}</pre>
    <nav>
      {numbered_links}
    </nav>
  </body>
  </html>
  """

# Route Handler: Retrieves or creates page
def handle(request):
    page = request.match_info.get('page')
    if(page.isnumeric()):
      try:
        page = int(page)
        if page < 0 or page >= PAGE_MAX:
          raise IndexError
        with open(f"page/{page}.txt", "r") as f:
          text = f.read()
          return web.Response(text=wrapHTML(text, page),
        content_type='text/html', status=200)
      except FileNotFoundError:
        text, before_text, after_text = create_page(page)
        return web.Response(text=wrapHTML(text, page),
        content_type='text/html', status=201, headers={'x-before': before_text, 'x-after': after_text})
      except IndexError:
        raise web.HTTPFound(f"/{randrange(PAGE_MAX)}")
      except Exception as e:
        return web.HTTPInternalServerError()
    else:
      raise web.HTTPFound(f"/{randrange(PAGE_MAX)}")

# Create application
app = web.Application()
# Add routes to application
app.add_routes([web.get('/', handleRandom),
                web.get('/{page}', handle)])
# Run application
if __name__ == '__main__':
    web.run_app(app)

