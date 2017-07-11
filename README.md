## Overview

[Hacker News](https://news.ycombinator.com/) copy that uses [Flask](http://flask.pocoo.org/) + [Jinja2](http://jinja.pocoo.org/docs/2.9/) for
routing and templating, [aiohttp](https://aiohttp.readthedocs.io/en/stable/) for asynchronous requests and [Hacker News REST API](https://github.com/HackerNews/API)
as source of data. In current state doesen't allow to view comments.

[Running version on Heroku](https://hn-flask.herokuapp.com/)

## Install locally

1. Clone or download.
2. `cd hn_flask`
3. It's better to run app in [virtual environment](https://virtualenv.pypa.io/en/stable/). If you have it installed run
`. venv/bin/activate`.
4. Istall app with `pip install --editable .`
5. Run app with `gunicorn hn_flask:app`
