from bs4 import BeautifulSoup
import requests as rq
import json 
import os
import string

class WarframeAcquisition():
    url = 'https://api.warframestat.us/'

    def __str__(self):
        return "Warframe Acquisition"
    
    def __init__(self):
        pass

    def queryMods (self,item_name):
        pass
    
    def getAllItems(self):
        site = rq.get('https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/All.json')
        # print(site.text)
        return site.json()
    
    def queryItems (self,item_name):
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
    
    def __init__(self):
        self.AllItems = self.getAllItems()
        
        
if __name__ == "__main__":
    access = WarframeAcquisition()
    access.queryItems('Wisp Prime')
    (access.parse_data('warframes'))
    access.getSubsections('warframes')
    print(access.subsections)
    (access.download_image)
    print(access.__str__())