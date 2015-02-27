import requests

from flask import Flask

app = Flask(__name__)


CONTENT_API_URL = 'http://content.guardianapis.com'
CONTENT_API_KEY = 'gnm-hackday'

DISCUSSION_API_URL = 'http://discussion.guardianapis.com/discussion-api'


@app.route('/')
def hello():

    return 'Hello World!'


if __name__ == '__main__':
    app.run()
