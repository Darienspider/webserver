import requests
import json
from bs4 import BeautifulSoup

class WarframeNews:
    def __init__(self):
        pass

    def getNews(self):
        news = {}
        url = 'https://www.warframe.com/search'
        response = requests.get(url)
        scanner = BeautifulSoup(response.content,'lxml')
        articles = scanner.find_all('div', class_='Card NewsCard')
        for article in articles:
            innerScanner = BeautifulSoup(str(article),'lxml')
            try:
                image_url = str(innerScanner.find('a', {'class':'Card-media'})['style']).replace('background-image: url(','').replace(');','')
            except:
                image_url = None
            title = innerScanner.find('div',{'class':'NewsCard-title'}).text
            postTime = str(innerScanner.find('div',{'class':'NewsCard-date'}).text).replace('Posted On ','')
            description = innerScanner.find('div',{'class':'NewsCard-description'}).text
            URL = innerScanner.find('div',{'class':'NewsCard-link'}).find('a')['href']
            tags = [i['data-platform'] for i in innerScanner.find_all('div',{'class':'PlatformTag'})]
            news[title] = {'image':image_url, 'postTime':postTime, 'description':description, 'URL':URL, 'tags':tags}
        return news


if __name__ == "__main__":
    api = WarframeNews()
    data = api.getNews()
    print(data.keys())