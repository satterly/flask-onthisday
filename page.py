#!/usr/bin/env python

import requests

CONTENT_API = 'http://content.guardianapis.com'
DISCUSSION_API = 'http://discussion.guardianapis.com/discussion-api'

url = CONTENT_API + '/search?api-key=r9fv4d8mpzngbvat2rkaeuez&from-date=2015-02-17T00:00:00%2b00:00&to-date=2015-02-25T14:59:00%2b00:00&show-fields=shortUrl,commentable&use-date=last-modified'
r = requests.get(url).json()

pages = r['response']['pages']


def info(results):
    for article in results:
        # print '%s %s' % (article['fields']['shortUrl'], article['sectionId'])

        key = article['fields']['shortUrl'].replace('http://gu.com', '')
        commentable = article['fields']['commentable'] == "true"
        section_id = article['sectionId']
        title = article['webTitle']

        # if '%' in title and commentable:
        #
        #     discussion_url = DISCUSSION_API + '/discussion' + key
        #     d = requests.get(discussion_url).json()
        #
        #     print '%s %s: %s -> %s' % (key, section_id, title, d['status'])

        if commentable:

            discussion_url = DISCUSSION_API + '/discussion' + key
            d = requests.get(discussion_url).json()

            if d['status'] == 'error':
                print '%s %s: %s -> %s' % (key, section_id, title, d['status'])

info(r['response']['results'])
for page in pages + 1):
    r = requests.get(url, params={'page': page}).json()
    info(r['response']['results'])
