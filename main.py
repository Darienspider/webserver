import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd 
import matplotlib.pyplot as plt
import time
from datetime import datetime
# personal class objects
from WarframeAPI.WarframeMarket import WarframeMarket
from WarframeAPI.WarframeAcquisition import WarframeAcquisition
from WarframeAPI.WarframeNews import WarframeNews



# from . import WarframeNews

#the "css" of the site is found in .streamlit/config.toml 
st.set_page_config(page_title='WebServer')

add_selectbox = st.sidebar.selectbox(
    "What App are we using today",
    ("Warframe Market", "Warframe Acquisition","Warframe News"),
    key='appSelection'
)
app_chosen = st.session_state['appSelection']

def graphVisual(table_title, data):

    # Graph visual
    dataframe = pd.DataFrame(data)
    if 'creation_date' not in dataframe.columns:
        st.warning("No 'creation_date' column found in the data.")
        return plt  # Early exit if column not found
    dataframe['creation_date'] = pd.to_datetime(dataframe['creation_date'],errors='coerce')
    dataframe = dataframe[dataframe['creation_date'] >= '2024-01-01']
    dataframe.set_index('creation_date', inplace=True)

    plt.figure(figsize=(20, 12))
    plt.scatter(dataframe.index, dataframe['platinum'], label='Platinum', alpha=0.9)
    plt.xlabel('Month')
    plt.ylabel('Total')
    plt.plot(dataframe.index, dataframe['platinum'], label='Platinum', alpha=0.9, color ='red')
    plt.legend()
    plt.title(f'{table_title}')
    return plt
            

def generateMarketContainer(item_name):
    """ Populates the container for the Warframe Market """
    if str(item_name).split()[-1].lower()== 'chassis' or str(item_name).split()[-1].lower()== 'systems' or str(item_name).split()[-1].lower()== 'neuroptics':
        item_name = item_name.strip() +' blueprint' #this fixes the need to add blueprint everytime
    if st.button("Generate Market data", key='generateMarketdata'): #if button is clicked
        extraction =api.getOrders(item_name=item_name)
        if extraction:
            #################### SELL ORDERS ####################
            df = pd.DataFrame(api.sell_orders)
            df = df[df['creation_date'] >= str(datetime.now().year)+'-01-01'] #cuttoff to only show details of previous year forward

            sell_recurring_price = str(df['platinum'].mode()[0])
            
            st.header(f"Sell Orders for {item_name}")
            st.write('The most recurring price is: ',sell_recurring_price,' plat')

            df.drop(columns=['visible','region','quantity','id','user'], inplace=True)
            
            st.dataframe(df)

            # GRID DESIGN
            st.title(f'Year to Date graph for {item_name}')

            graph_title = f'Sell orders for {str(item_name).capitalize()}'
            plt2 = graphVisual(graph_title, df)
            st.pyplot(plt2)

            #################### BUY ORDERS ####################
   
            buying_df = pd.DataFrame(api.buy_orders)
            buying_df = buying_df[buying_df['creation_date'] >= str(datetime.now().year)+'-01-01'] #cuttoff to only show details of previous year forward
            buying_df.drop(columns=['visible','region','quantity','id','user'], inplace=True)

            st.header(f"Buy Orders for {item_name}")
            st.write('The most recurring price is: ',str(buying_df['platinum'].mode()[0]),' plat')
            st.dataframe(buying_df)

            # Graph visual
            st.title(f'Year to Date graph for {item_name}')
            
            graph_title = f'Buy orders for {str(item_name).capitalize()}'
            plt = graphVisual(graph_title, buying_df)
            st.pyplot(plt)


def acquisitionData(item_name):
    api = WarframeAcquisition()
    api.queryItems(item_name)
    api.getCategories()
    add_buttons = st.radio('Choose Item Type',
                           options=[i for i in api.categories],
                           key = 'AcquisitionSectionToParse'

    )
    api.parse_data(section=st.session_state['AcquisitionSectionToParse'])
    api.getSubsections(section=st.session_state['AcquisitionSectionToParse'])
    for i in api.subsections:
        subsection = st.session_state['AcquisitionSectionToParse']
        if api.extracted:
            doubleWords = {
                'Imagename': 'Image Name',
                'Isprime': 'Primed',
                'Levelstats': 'Stats',
                'Fusionlimit': 'Fusion Limit',
                'Releasedate': 'Release Date',
                'Wikiaurl': 'Wiki Link',
                'Passivedescription': 'Passive Ability Description',
                'Masteryreq': 'Mastery Requirement',
                'Buildprice': 'Build Price',
                'Buildquantity': 'Build Quantity',
                'Productcategory': 'Product Category',
                'Skipbuildtimeprice': 'Skip Build Time Price',
                'Sprintspeed': 'Sprint Speed',
                'Consumeonbuild': 'Consume On Build',
                'Showininventory': 'Show in Inventory'
            }
            # convert buildtime to something more readable
            if str(i).lower() == 'buildtime':
                build_Value = (api.extracted[0][i])
                days, seconds = divmod(build_Value, 86400) 
                hours, seconds = divmod(build_Value, 3600)
                minutes, seconds = divmod(build_Value, 60)
                st.write(f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds")

        
            elif str(i).lower() == 'wikiathumbnail':
                # st.image()pass
                st.header('Thumbnail')
                image_url = str(api.extracted[0][i])+'.jpg'
                image_path = api.download_image(image_url, item_name)
                st.image(str(image_path))
            
            # using dictionary and list comprehension to lessen the number of elif statements required to update headers
            elif (str(i).lower() in [str(x).lower() for x in doubleWords.keys()]):
                st.header(doubleWords[(str(i).capitalize())])
                st.write(api.extracted[0][i])

            else:
                st.header(str(i).capitalize())
                st.write(api.extracted[0][i])

def gatherNews():
    api = WarframeNews()
    data = api.getNews()
    for i in data.keys():
        st.header(i)
        st.write(
            (datetime.strftime(
                datetime.strptime(
                    data[i]['postTime'],
                    '%Y-%m-%d %H:%M:%S'),
            '%B %d, %Y %I:%M %p')
            )
        )

        st.write(data[i]['description'])
        if len(data[i]['tags']) > 0:
            st.write(data[i]['tags'])
        st.write(data[i]['URL'])
        st.image(data[i]['image'])
        st.write('-----------------------------------')

if app_chosen =='Warframe News':
    st.title('Warframe News')
    st.write('This page provides a list of the latest news from Warframe')
    api = WarframeNews
    gatherNews()











# WARFRAME MARKET SECTION
if app_chosen =='Warframe Market':
    st.title("Warframe Market")
    st.write("This screen allows users to dunamically scan warframes market for pricing based on data entered in Item name field below: ")
    st.write("If you do not see a button after entering an item name, hit the enter key on your keyboard :smile: ")
    api = WarframeMarket()
    with st.container():
        st.text_input("Insert Item Name: ", placeholder="Item Name here",key='warframeMarketInput')
        item_name = str(st.session_state['warframeMarketInput']).lower()
        if item_name:
            try:
                generateMarketContainer(item_name)
            except:
                st.write('Item not found')

        else:
            pass            
            
        # CHATBOT SECTION

# WARFRAME WIKI / Acquisition Section
if app_chosen =='Warframe Acquisition':
    st.title('Acquisition Screen')
    st.write('This will be a wiki page personally designed by me. It will allow users to dynamically populate this page with content from whatever item')
    api = WarframeAcquisition()
    with st.container():
        st.text_input("Insert Item Name: ", placeholder="Item Name here",key='WarfraneAcquisitionInput')
        item_name = str(st.session_state['WarfraneAcquisitionInput']).lower()
        if item_name:
            acquisitionData(item_name)
        else:
            pass            

