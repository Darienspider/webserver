import json
import requests as rq
import pandas as pd
class WarframeMarket():
    link = 'https://api.warframe.market/v2'
    def __init__(self):
        pass
    
    def __str__(self):
        return "Warframe Market"
    
    def item_orders (self,item_name):
        if str(item_name).split()[-1].lower()== 'chassis' or str(item_name).split()[-1].lower()== 'systems' or str(item_name).split()[-1].lower()== 'neuroptics':
            item_name = item_name.strip() +' blueprint' #this fixes the need to add blueprint everytime
        
        if str(item_name).split()[-1].lower() == 'prime':
            item_name = item_name.strip() +' set' #this fixes the need to add 'prime' everytime
        
        item_name = str(item_name).replace(' ','_')
        print(item_name)
        site = rq.get(f'{self.link}/orders/item/{item_name}')
        self.all_orders = json.loads(site.content)
        return self.all_orders

    def getOrders(self,item_name):
        if str(item_name).split()[-1].lower()== 'chassis' or str(item_name).split()[-1].lower()== 'systems' or str(item_name).split()[-1].lower()== 'neuroptics':
            item_name = item_name.strip() +' blueprint' #this fixes the need to add blueprint everytime  
        
        payload = self.item_orders(f'{item_name}')['data']

        # print(payload)
        self.buy_orders = []
        self.sell_orders = []

        for order in payload:
            if str(order['type']).lower() == 'sell':
                self.sell_orders.append(order)
                
            if str(order['type']).lower() == 'buy':
                self.buy_orders.append(order)

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
                    
if __name__ == "__main__":
    item_name = 'wisp prime'
    # item_name = input('Please enter Item name: ')
    # typeOfData = input('')
    api = WarframeMarket()
    api.getOrders(item_name)
    print((api.buy_orders[0]))

    
