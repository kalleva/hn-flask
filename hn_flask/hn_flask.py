from flask import Flask, render_template, request
import httplib2
import json
import datetime
import asyncio
from aiohttp import ClientSession
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

app = Flask(__name__)

hn_api_urls = {
    'item_url':
    'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty',
    'top_stories':
    'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty',
    'new_stories':
    'https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty',
    'best_stories':
    'https://hacker-news.firebaseio.com/v0/bestsories.json?print=pretty',
    'ask_stories':
    'https://hacker-news.firebaseio.com/v0/askstories.json?print=pretty',
    'show_stories':
    'https://hacker-news.firebaseio.com/v0/showstories.json?print=pretty',
    'job_stories':
    'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty'
}

h = httplib2.Http('.cache')

hn_site_links = {
    'top_url': '/',
    'show_url': '/show',
    'new_url': '/newest',
    'ask_url': '/ask',
    'jobs_url': '/jobs'
}

loop = asyncio.get_event_loop()


@app.route('/')
@app.route('/news')
def top_pages():
    return create_template('top_stories', 'top')


@app.route('/show')
def show_pages():
    return create_template('show_stories', 'show')


@app.route('/newest')
def new_pages():

    return create_template('new_stories', 'new')


@app.route('/jobs')
def job_pages():
    return create_template('job_stories', 'job')


@app.route('/ask')
def ask_pages():
    return create_template('ask_stories', 'ask')


def create_template(link_type, destination):
    """
    Create template based on url and additional info on number of elements
    request to API returns.
    """
    p = request.args.get('p')
    if p:
        page = int(p)
    else:
        page = 1
    m = more_url(request.url, page)
    top_stories = fetch_stories(link_type)
    current_page_stories = add_properties(
        fetch_content_current_page_stories(
            top_stories[(page - 1) * 30: page * 30]), (page - 1) * 30 + 1)
    if len(current_page_stories) == 30:
        return render_template('index.html.j2',
                               stories=current_page_stories, no_more=False,
                               more=m, site_links=hn_site_links,
                               link_dest=destination)
    else:
        return render_template('index.html.j2',
                               stories=current_page_stories, no_more=True,
                               more=m, site_links=hn_site_links,
                               link_dest=destination)


def fetch_stories(theme):
    """Fetch list of ids of stories from API on theme subject."""
    response, content = h.request(hn_api_urls[theme])
    if response.status == 200:
        return list(json.loads(content, encoding='utf-8'))
    else:
        raise Exception("Wasn't able to fetch stories")


def fetch_content_current_page_stories(ids):
    """Asynchroniously fetch info from API for every element in list of ids."""

    # use this record to restore inital order of stories, after we accuire them
    # asynchroniously in unpredictable order
    record_of_stories = {key: '' for key in ids}
    future = asyncio.ensure_future(run(ids, record_of_stories))
    loop.run_until_complete(future)

    # at this point record_of_stories containd all requested stories
    # all we need to do is to take them out in order in which corresponding
    # id lives in ids list
    stories = []
    for id in ids:
        stories.append(record_of_stories[id])
    return stories


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


async def run(ids, record):
    tasks = []
    async with ClientSession() as session:
        for id in ids:
            task = asyncio.ensure_future(
                fetch(hn_api_urls['item_url'].format(id), session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        for story in responses:
            i = json.loads(story, encoding='utf-8')
            record[i['id']] = i


def add_properties(stories, start=1):
    """Add time in hours since article was posted and number of comments."""
    for i, story in enumerate(stories):
        p = (datetime.datetime.now() -
             datetime.datetime.fromtimestamp(int(story['time'])))
        story['time_since_posted'] = str(p.days * 24 + p.seconds // 3600)
        story['index'] = str(i + start)
        if 'kids' in story.keys():
            story['comments'] = str(len(story['kids']))
        else:
            story['comments'] = '0'
        if 'url' in story.keys():
            story['site_name'] = urlparse(story['url']).netloc
        else:
            story['url'] = (r'https://news.ycombinator.com/item?id=' +
                            str(story['id']))
            story['site_name'] = ''
    return stories


def more_url(url, page):
    """Return url for More link."""
    params = {'p': str(page + 1)}
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)
