from aiohttp import web
from random import randrange
from jinja2 import Environment, FileSystemLoader
from settings import PAGE_MAX, PAGE_REACH, PAGE_PATH
from client import create_text
from util import read_file, write_file
from pyquery import PyQuery

# d = PyQuery('<!DOCTYPE html><html><body><p>Hello</p></body></html>')
# print(d('p').text())

# Prompts
prompt_env = Environment(loader=FileSystemLoader('prompt'))
prompts = list(map(lambda name: prompt_env.get_template(f"{name}.txt"), ["first", "mid", "last"]))

# Templates
template = Environment(loader=FileSystemLoader('templates')).get_template('story.html')

# Retrieves page. Generates text if none exists.
def get_page(page, reach=PAGE_REACH):
  pages_previous, pages_next = [], []
  base_path = PAGE_PATH
  text = read_file(PAGE_PATH / f"{page}.html")
  if text:
    return text, None, None, 200
  for i in range(1, reach + 1):
      file_path = base_path / f"{page - i}.html"
      if file_path.exists():
          pq = PyQuery(file_path.read_text())
          pages_previous.insert(0, pq('pre').text())  # Insert at beginning to maintain order
      else:
          break  # Stop if a gap is found
  # Check and collect pages immediately after the current page
  for i in range(1, reach + 1):
      file_path = base_path / f"{page + i}.html"
      if file_path.exists():
          pq = PyQuery(file_path.read_text())
          pages_next.append(pq('pre').text())
      else:
          break  # Stop if a gap is found
  previous = "\n".join(pages_previous)
  next = "\n".join(pages_next)

  prompt = prompts[0 if page == 0 else 2 if page == PAGE_MAX - 1 else 1].render(previous=previous, next=next)

  links_html = ''.join(
    [f'<a href="/{i+1}" title="page:{i+1}">{i+1}</a>' for i in range(PAGE_MAX)]
  )

  text = write_file(
      f"page/{page}.html",
      template.render(text=create_text(prompt), index=page, links=links_html, max_pages=PAGE_MAX))
  return text, previous.replace("\n", ""), next.replace("\n", ""), 201

# Request Handler: Retrieves page. Generates text if none exists. Redirects if url is invalid.
async def handle(request):
  page = request.match_info.get('page')

  if not page or not page.isdigit() or not (0 < int(page) <= PAGE_MAX):
    print("Page:", page)
    raise web.HTTPFound(f"/{randrange(PAGE_MAX) + 1}")

  page = int(page) - 1
  text, previous, next, status_code = get_page(page)

  response = web.Response(text=text, status=status_code, content_type='text/html')

  if previous:
    response.headers['x-previous'] = previous.replace('\n', ' ')
  if next:
    response.headers['x-next'] = next.replace('\n', ' ')
  return response

# Create application
app = web.Application()
# Add routes to application
app.add_routes([
  web.get('/favicon.ico',
          lambda _: web.Response(status=200, content_type='image/x-icon')),
  web.get('/', handle),
  web.get('/{page}', handle)])
# Run application
if __name__ == '__main__':
    web.run_app(app)

