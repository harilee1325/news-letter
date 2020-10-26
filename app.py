from bs4 import BeautifulSoup
import requests
import urllib
import json
import re
from flask import Flask, request
import json as simplejson
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)


@app.route("/get-news/<string:keyword>/<string:page>", methods=['GET'])
def get_news(keyword, page):
    try:
        data = get_news(keyword.replace(' ', ''), page)
        return dumps({'success': 'yes', 'news': data})
    except Exception as e:
        return dumps({'error': str(e)})


@app.route("/get-news-from-tags/<string:keyword>", methods=['GET'])
def get_news_from_tags(keyword):
    try:
        keywords = keyword.split(',').replace(' ', '')
        data = get_tag_news(keywords)
        return dumps({'success': 'yes', 'news': data})
    except Exception as e:
        return dumps({'error': str(e)})


def get_tag_news(keywords):

    print(keywords)
    tagArray = []
    for key in keywords:
        # news = {
        #     key: get_news(key, "0")
        # }
        tagArray.append(get_news(key, "0"))

    print(tagArray)
    return tagArray


def get_news(keyword, page):
    source=requests.get(
            'https://www.google.com/search?q='+keyword+'&tbm=nws&start='+page).text


    soup=BeautifulSoup(source, 'lxml')

    images=[]


    class NewsData:

        def __init__(self, headline, image, description, time, link, author):
            self.headline=headline
            self.image=image
            self.description=description
            self.time=time
            self.link=link
            self.author=author


    newsArray=[]
    scripts=str(soup.find_all('script')).split('(function(){var')
    for script in scripts:
        if (script.find('data:image/') != -1):
            index=script.find(';var i=')
            img=script.replace("s='", '')[:index-4]
            new_index=img.find('\\')
            # print(img[:new_index])
            images.append(img[:new_index])

    i=0
    for div in soup.find_all('div', class_='ZINbbc xpd O9g5cc uUPGi'):

        try:
            headline=div.div.a.h3.div.text
            by=div.find('div', class_='BNeawe UPmit AP7Wnd').text
            time=div.find(
                'div', class_='BNeawe s3v9rd AP7Wnd').div.div.span.text
            desc=div.find('div', class_='BNeawe s3v9rd AP7Wnd').div.div.text
            link=div.div.a['href'].replace('/url?q=', '').split('&sa=')
            image=images[i]
            i += 1

        except Exception as e:
            headline, by, time, desc, link[0], image=None

        news=NewsData(headline, image, desc, time, link[0], by)
        newsArray.append(news)


    newsJsonArray=[]
    for news in newsArray:

        news_json={
            'headline': news.headline,
            'author': news.author,
            'image': news.image,
            'desc': news.description.replace(news.time, ''),
            'time': news.time,
            'link': news.link
        }
        newsJsonArray.append(news_json)

    return newsJsonArray


if __name__ == '__main__':
    app.run()
