import os
import requests

from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, jsonify

app = Flask(__name__)


CONTENT_API_URL = 'https://content.guardianapis.com'
CONTENT_API_KEY = os.environ.get('CONTENT_API_KEY', 'test')

DISCUSSION_API_URL = 'https://discussion.guardianapis.com/discussion-api'


def get_comment_counts(keys):

    try:
        url = '%s/getCommentCounts?short-urls=%s' % (DISCUSSION_API_URL, ','.join(keys))
        counts = requests.get(url).json()
    except Exception as e:
        return str(e)

    print counts

    return counts


def get_articles(year, month, day):

    from_date = '%s-%02d-%02dT00:00:00' % (year, month, day)
    to_date = '%s-%02d-%02dT23:59:59' % (year, month, day)

    fields = ['headline', 'shortUrl', 'trailText', 'thumbnail', 'byline', 'standfirst']

    r = 'foo'
    try:
        url = '%s/search?api-key=%s&from-date=%s&to-date=%s&use-date=published&show-fields=%s&page-size=100&commentable=true' % \
              (CONTENT_API_URL, CONTENT_API_KEY, from_date, to_date, ','.join(fields))
        r = requests.get(url)
        json = r.json()
        results = json['response']['results']
    except Exception:
        raise RuntimeError(r.text)
    counts = get_comment_counts([a['fields']['shortUrl'].replace('https://gu.com', '') for a in results])

    for article in results:
        key = article['fields']['shortUrl'].replace('https://gu.com', '')
        article['comments'] = counts.get(key, 0)

    pages = json['response']['pages']
    for page in range(2, pages+1):
        content = requests.get(url, params={'page': page}).json()
        next = content['response']['results']

        counts = get_comment_counts([a['fields']['shortUrl'].replace('https://gu.com', '') for a in next])
        for article in next:
            key = article['fields']['shortUrl'].replace('https://gu.com', '')
            article['comments'] = counts.get(key, 0)
        results += next

    return results


@app.route('/')
def index():

    return redirect(url_for('today'))

@app.route('/today')
def today():

    today = datetime.today()
    return redirect('/%s' % today.strftime("%Y/%m/%d"))

@app.route('/<int:year>/<int:mon>/<int:day>')
def onthisday(year, mon, day):

    try:
        this_day = datetime(year, mon, day)
        month = this_day.strftime('%B')
        weekday = this_day.strftime('%A')
    except ValueError as e:
        return render_template('error.html', message=str(e)), 400

    yesterday = (this_day - timedelta(days=1)).strftime("%Y/%m/%d")

    try:
        articles = get_articles(year, mon, day)
    except Exception as e:
        return render_template('error.html', error=str(e))

    #return jsonify(articles=sorted(articles, key=lambda k: k['comments'], reverse=True))

    return render_template('onthisday.html', weekday=weekday, day=day, month=month, year=year, yesterday=yesterday, articles=sorted(articles, key=lambda k: k['comments'], reverse=True)[:10])


if __name__ == '__main__':
    app.run(debug=True)
