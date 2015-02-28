import requests

from datetime import datetime
from flask import Flask, render_template, redirect, url_for, jsonify

app = Flask(__name__)


CONTENT_API_URL = 'http://content.guardianapis.com'
CONTENT_API_KEY = 'test'

DISCUSSION_API_URL = 'http://discussion.guardianapis.com/discussion-api'


def get_comment_counts(keys):

    try:
        url = '%s/getCommentCounts?short-urls=%s' % (DISCUSSION_API_URL, ','.join(keys))
        counts = requests.get(url).json()
    except Exception as e:
        return str(e)

    return counts


def get_articles(year, month, day):

    from_date = '%s-%02d-%02dT00:00:00' % (year, month, day)
    to_date = '%s-%02d-%02dT23:59:59' % (year, month, day)

    fields = ['headline', 'shortUrl', 'trailText', 'thumbnail', 'byline', 'standfirst']

    #try:
    url = '%s/search?api-key=%s&from-date=%s&to-date=%s&use-date=published&show-fields=%s&page-size=100' % \
          (CONTENT_API_URL, CONTENT_API_KEY, from_date, to_date, ','.join(fields))
    content = requests.get(url).json()
    #except Exception as e:
    #    return str(e)
    results = content['response']['results']
    counts = get_comment_counts([a['fields']['shortUrl'].replace('http://gu.com', '') for a in results])

    for article in results:
        key = article['fields']['shortUrl'].replace('http://gu.com', '')
        article['comments'] = counts.get(key, 0)

    pages = content['response']['pages']
    for page in range(2, pages+1):
        content = requests.get(url, params={'page': page}).json()
        next = content['response']['results']

        counts = get_comment_counts([a['fields']['shortUrl'].replace('http://gu.com', '') for a in next])
        for article in next:
            key = article['fields']['shortUrl'].replace('http://gu.com', '')
            article['comments'] = counts.get(key, 0)
        results += next

    return results


@app.route('/')
def index():

    return redirect(url_for('today'))

@app.route('/today')
def today():

    today = datetime.today()

    return onthisday(today.year, today.month, today.day)

@app.route('/<int:year>/<int:month>/<int:day>')
def onthisday(year, month, day):

    this_day = datetime(year, month, day)
    articles = get_articles(year, month, day)

    #return jsonify(articles=sorted(articles, key=lambda k: k['comments'], reverse=True))

    return render_template('onthisday.html', weekday=this_day.strftime('%A'), day=day, month=this_day.strftime('%B'), year=year, articles=sorted(articles, key=lambda k: k['comments'], reverse=True)[:10])


if __name__ == '__main__':
    app.run(debug=True)
