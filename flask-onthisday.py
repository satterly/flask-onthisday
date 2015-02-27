import requests

from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)


CONTENT_API_URL = 'http://content.guardianapis.com'
CONTENT_API_KEY = 'gnm-hackday'

DISCUSSION_API_URL = 'http://discussion.guardianapis.com/discussion-api'


@app.route('/today')
def today():

    today = datetime.today()
    return onthisday(today.year, today.month, today.day)

@app.route('/<int:year>/<int:month>/<int:day>')
def onthisday(year, month, day):


    this_day = datetime(year, month, day)

    try:
        from_date = '%s-%02d-%02d' % (year, month, day)
        to_date = '%s-%02d-%02d' % (year, month, day+1)

        fields = ['headline', 'shortUrl', 'trailText', 'thumbnail', 'byline', 'standfirst']

        url = '%s/search?api-key=%s&from-date=%s&to-date=%s&use-date=published&show-fields=%s&page-size=100' % \
              (CONTENT_API_URL, CONTENT_API_KEY, from_date, to_date, ','.join(fields))
        content = requests.get(url).json()
    except Exception as e:
        return str(e)

    articles = content['response']['results']
    keys = [a['fields']['shortUrl'].replace('http://gu.com', '') for a in articles]

    try:
        url = '%s/getCommentCounts?short-urls=%s' % (DISCUSSION_API_URL, ','.join(keys))
        counts = requests.get(url).json()
    except Exception as e:
        return str(e)

    for article in articles:
        key = article['fields']['shortUrl'].replace('http://gu.com', '')
        article['comments'] = counts.get(key, 0)

    #return jsonify(articles=sorted(articles, key=lambda k: k['comments'], reverse=True))

    return render_template('onthisday.html', weekday=this_day.strftime('%A'), day=day, month=this_day.strftime('%B'), year=year, articles=articles[:5])


if __name__ == '__main__':
    app.run(debug=True)
