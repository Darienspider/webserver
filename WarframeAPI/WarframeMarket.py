import json
import requests as rq
import pandas as pd
class WarframeMarket():
    link = 'https://api.warframe.market/v1'
    def __init__(self):
        pass
    
    def __str__(self):
        return "Warframe Market"
    
    def items(self,item_name):

        item_name = str(item_name).replace(' ','_')
        site = rq.get(str(self.link) +f'/items/{item_name}')
        return json.loads(site.content)

    def item_orders (self,item_name):
        item_name = str(item_name).replace(' ','_')
        site = rq.get(str(self.link) +f'/items/{item_name}/orders')
        return json.loads(site.content)

    def getOrders(self,item_name):
        payload = self.item_orders(f'{item_name}')['payload']['orders']
        # print(payload)
        self.buy_orders = []
        self.sell_orders = []

        for order in payload:
            if str(order['order_type']).lower() == 'sell':
                self.sell_orders.append(order)
            else:
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

if __name__ == "__main__":
    item_name = 'wisp prime systems blueprint'
    api = WarframeMarket()
    api.getOrders(item_name)
    # print(api.buy_orders)
    pricees = api.recurringPrices()
    print(pricees)