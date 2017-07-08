from flask import Flask, render_template, request
import httplib2
import json
import datetime
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

# fix before prod
hn_site_links = {
    'show_url': 'https://hn-flask.herokuapp.com/show',
    'top_url': 'https://hn-flask.herokuapp.com/',
    'new_url': 'https://hn-flask.herokuapp.com/newest',
    'ask_url': 'https://hn-flask.herokuapp.com/ask',
    'jobs_url': 'https://hn-flask.herokuapp.com/jobs'
}


@app.route('/')
@app.route('/news')
def top_pages():
    return create_template('top_stories', 10, 'top')


@app.route('/show')
def show_pages():
    return create_template('show_stories', 6, 'show')


@app.route('/newest')
def new_pages():
    return create_template('new_stories', 10, 'new')


@app.route('/jobs')
def job_pages():
    return create_template('job_stories', 6, 'job')


@app.route('/ask')
def ask_pages():
    return create_template('ask_stories', 6, 'ask')


def create_template(link_type, max_page, destination):
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
    """Fetch info from API for every element in list of ids."""
    stories = []
    for id in ids:
        response, content = h.request(hn_api_urls['item_url'].format(id))
        if response.status == 200:
            stories.append(dict(json.loads(content)))
    return stories


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
        # todo: fix no script issue when there is no links, currently hotfix
        if 'url' in story.keys():
            story['site_name'] = urlparse(story['url']).netloc
        else:
            story['url'] = (r'https://news.ycombinator.com/item?id=' +
                            str(story['id']))  # hotfix
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
