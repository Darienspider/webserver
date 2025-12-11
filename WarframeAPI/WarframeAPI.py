from bs4 import BeautifulSoup
import requests as rq
import json 
import os
import string
import json
import pandas as pd

# TODO: Condense all of the warframe components into 1 Main API script
class WarframeAPI:
    def __init__(self):
        self.marketUrl = 'https://api.warframe.market/v1'
        self.acquisitionUrl = 'https://api.warframestat.us/'
        
    def __str__(self):
        return 'Warframe Main API'
    
    def getAllItems(self):
        site = rq.get('https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/All.json')
        # print(site.text)
        return site.json()
    def gathernews(self):
        news = {}
        url = 'https://www.warframe.com/search'
        response = rq.get(url)
        scanner = BeautifulSoup(response.content,'lxml')
        articles = scanner.find_all('div', class_='Card NewsCard')
        for article in articles:
            innerScanner = BeautifulSoup(str(article),'lxml')
            image_url = str(innerScanner.find('a', {'class':'Card-media'})['style']).replace('background-image: url(','').replace(');','')
            title = innerScanner.find('div',{'class':'NewsCard-title'}).text
            postTime = str(innerScanner.find('div',{'class':'NewsCard-date'}).text).replace('Posted On ','')
            description = innerScanner.find('div',{'class':'NewsCard-description'}).text
            URL = innerScanner.find('div',{'class':'NewsCard-link'}).find('a')['href']
            tags = [i['data-platform'] for i in innerScanner.find_all('div',{'class':'PlatformTag'})]
            news[title] = {'image':image_url, 'postTime':postTime, 'description':description, 'URL':URL, 'tags':tags}
        return news  
     
    # WARFRAME Intel / Acquisition 
    class Intel:
        def __init__(self,acquisitionUrl):
            self.link = acquisitionUrl
            
        def queryMarketItems (self,item_name):
            self.link =rq.get(f'https://api.warframestat.us/items/search/{item_name}')
            if self.link.status_code ==200: #successful
                self.data = json.loads(self.link.content)
            else:
                self.data = 'No Data Returned'

            return self.data

        def getCategories(self ):
            data = self.data
            self.categories = []
            for i in data:
                if str(i['category']) not in self.categories:
                    self.categories.append(i['category'])
        
        def getSubsections(self,section):
            data = self.data
            self.subsections = []
            self.parse_data(section)
            try:
                for i in self.extracted[0]:
                    self.subsections.append(i)
            except IndexError as e:
                self.subsections = ''
                return  self.subsections
                
        def parse_data (self, section):
            data = self.data
            self.extracted = []
            for i in data:
                if str(i['category']).lower()  ==  str(section).lower():
                    self.extracted.append(i)
        
        def download_image(self, url, item_name):
            # Ensure that item_name is sanitized
            item_name = str(item_name).replace(' ', '_')
            
            # Define the directory and filename
            directory = 'images'
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            filename = os.path.join(directory, f'{item_name}.jpg')
            
            # Download the image and save it
            data = rq.get(url, stream=True)
            with open(filename, 'wb') as output_file:
                output_file.write(data.content)
            return filename         
               
        def getResourceImage(self,item_name):
            site = rq.get('https://warframe.fandom.com/wiki/Category:Resource_Photo',stream=True)
            print(site.status_code)
            resources = {}
            names_gathered = []
            if site.status_code ==200:
                print('Success')
                scanner = BeautifulSoup(site.content,'lxml')
                resource_panel = scanner.find_all('li',{'class':"category-page__member"})
                for resources in resource_panel:
                    # print(resources)
                    innerScanner = BeautifulSoup(str(resources),'lxml')
                    resource_image_tag = innerScanner.find('div',{'class':'category-page__member-left'})
                    resource_name = str(innerScanner.find('a',{'class':'category-page__member-link'}).text).replace('File:','')
                    
                    # if statement here
                    # if str(item_name).replace(' ','').lower().strip() == 'controlmodule':
                    if str(item_name).lower().replace(' ','') in str(resource_name).replace(' ','').replace('.png','').replace('64.png','').lower().strip():
                        names_gathered.append(resource_name)
                        image_url = str(resource_image_tag.img).split()[-1].replace('src="','').replace('"/>','')
                        try:
                            resource_image = rq.get(image_url).content
                            with open(f'images/{resource_name}','wb') as downloaded_data:
                                downloaded_data.write((resource_image))
                                downloaded_data.close()
                        except: 
                            print(f'resource name: {resource_name} not found')
                            
            return names_gathered
        def riven_disposition (self):
            dispo_site = 'https://warframe.fandom.com/wiki/Riven_Mods/Weapon_Dispos/All'
            
            
    # Warframe Market 
    class Market():
        def __init__(self,marketUrl):
            self.link = marketUrl
            pass
        
        def items(self,item_name):
            item_name = str(item_name).replace(' ','_')
            site = rq.get(str(self.link) +f'/items/{item_name}')
            return json.loads(site.content)

        def item_orders (self,item_name):
            if str(item_name).split()[-1].lower()== 'chassis' or str(item_name).split()[-1].lower()== 'systems' or str(item_name).split()[-1].lower()== 'neuroptics':
                item_name = item_name.strip() +' blueprint' #this fixes the need to add blueprint everytime  
                
            item_name = str(item_name).replace(' ','_')
            site = rq.get(str(self.link) +f'/items/{item_name}/orders')
            print(str(self.link) +f'/items/{item_name}/orders')
            return json.loads(site.content)
        
        def getOrders(self,item_name):
            if str(item_name).split()[-1].lower()== 'chassis' or str(item_name).split()[-1].lower()== 'systems' or str(item_name).split()[-1].lower()== 'neuroptics':
                item_name = item_name.strip() +' blueprint' #this fixes the need to add blueprint everytime  

            
            payload = self.item_orders(f'{item_name.lower()}')['payload']['orders']
            # print(payload)
            self.buy_orders = [order for order in payload if order['order_type'] != 'sell']
            self.sell_orders = [order for order in payload if order['order_type'] == 'sell']

            if len(self.buy_orders) > 0 or len(self.sell_orders) > 0:
                return True
            else:
                return False

        def recurringPrices(self,data):
            """Finds the most recurring price in the given data."""
            # Check if data is a DataFrame or Series, handle accordingly
            if isinstance(data, pd.DataFrame):
                plat_list = data['platinum'].tolist()
            elif isinstance(data, pd.Series):
                plat_list = data.tolist()
            else:
                plat_list = [order['platinum'] for order in data]

            recurring_price = max(set(plat_list), key=plat_list.count)
            return recurring_price

        def rivenMarket(self,item_name):
            found_items = []
            riven_parse_site = 'https://www-static.warframe.com/repos/weeklyRivensPC.json'
            content = rq.get(riven_parse_site)

            if content.status_code == 200:
                rivens = (json.loads(content.content))

            for i in rivens:
                if f'{str(item_name).lower()}' in str(i['compatibility']).lower():
                    found_items.append(i)
            
            if len(found_items) < 1:
                return None
            else:
                    return found_items
                    
