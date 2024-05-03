from aiohttp import web
from random import randrange
from jinja2 import Environment, FileSystemLoader
from settings import PAGE_MAX, PAGE_REACH, PAGE_PATH, SITE_ROOT
from client import create_text
from util import read_file, write_file, glob_count
from pyquery import PyQuery

# Prompts
prompt_env = Environment(loader=FileSystemLoader('prompt'))
prompts = list(map(lambda name: prompt_env.get_template(f"{name}.txt"), ["first", "mid", "last"]))

# Templates

links = ''.join(
  [f'<a href="/{i}.html" title="page:{i}">{i}</a>' for i in range(PAGE_MAX+1)]
)
template = Environment(loader=FileSystemLoader('templates')).get_template('story.html')


# Retrieves page. Generates text if none exists.
def get_page(page, reach=PAGE_REACH):
  base_path = PAGE_PATH
  text = read_file(PAGE_PATH / f"{page}.html")
  if text is not None:
    return text, None, None, 200
  if(page == 0):
    raise FileNotFoundError
  pages_previous, pages_next = [], []
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

  prompt = prompts[0 if page == 1 else 2 if page == PAGE_MAX else 1].render(previous=previous, next=next)

  text = write_file(
      f"page/{page}.html",
      template.render(
        pres=create_text(prompt),
        index=page,
        links=links,
        max_pages=PAGE_MAX))
  return text, previous.replace("\n", ""), next.replace("\n", ""), 201


# Combines all html content and saves it to a file, 0.html
def combine_and_save_text():
  text = []
  for i in range(1, PAGE_MAX + 1):
    pq = PyQuery(read_file(PAGE_PATH / f"{i}.html"))
    text.append(pq('pre').html())

  write_file(PAGE_PATH / "0.html",template.render(
        pres='\n\n'.join(text),
        index=0,
        links=links,
        max_pages=PAGE_MAX) )

# Request Handler: Retrieves page. Generates text if none exists. Redirects if url is invalid.
async def handle(request):
  page = request.match_info.get('page')
  # convert page to int
  try:
    page = int(page)
  except Exception as e:
    page = None
  # Reirect to random endpoint if page is invalid
  if page is None or not (0 <= page <= PAGE_MAX):
    raise web.HTTPFound(f"/{randrange(PAGE_MAX) + 1}.html")
  # retrieve cached page or generate new page
  try:
    text, previous, next, status = get_page(page)
  except FileNotFoundError:
    raise web.HTTPFound(f"/{randrange(PAGE_MAX) + 1}.html")
  # create response using page text

  response = web.Response(
    text=text,
    status=status,
    content_type='text/html')
  # add content if it was just used to generate currently viewed page
  if previous:
    response.headers['x-previous'] = previous.replace('\n', ' ')
  if next:
    response.headers['x-next'] = next.replace('\n', ' ')

  if(status == 201):
    count = glob_count("page/*.html")
    print(f"Created Files: {count}/{PAGE_MAX}")
    if count == PAGE_MAX:
      print(f"All {count} files created. Combining...")
      combine_and_save_text()
      raise web.HTTPFound(f"/0.html")

  return response
# Create application
app = web.Application()
# Add routes to application
app.add_routes([
  web.get(f'{SITE_ROOT}favicon.ico',
          lambda _: web.Response(content_type='image/x-icon')),
  web.get(f'{SITE_ROOT}', handle),
  web.get(f'{SITE_ROOT}{{page}}.html', handle),
  web.get(f'{SITE_ROOT}{{page}}', handle)])
# Run application
if __name__ == '__main__':
    web.run_app(app)

