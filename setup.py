from setuptools import setup

setup(
    name='hn_flask',
    packages=['hn_flask'],
    include_package_data=True,
    install_requires=[
        'flask',
        'click',
        'gunicorn',
        'httplib2',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'Werkzeug',
        'aiohttp'
    ],
)
