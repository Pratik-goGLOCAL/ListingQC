import pandas as pd
import numpy as np
import os
import streamlit as st
import pickle as pkl
import pandas as pd
import subprocess
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
# from spellchecker import SpellChecker
from loguru import logger
from fuzzywuzzy import fuzz
# from excel_checks import QC_check1
import sys

st.set_page_config(
    page_title="Listing QC"
)

st.title("ListingQC")
# st.sidebar.success("Select Action")

### AUTH
with open('DataStore/auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name,authentication_status,username = authenticator.login('Login','main')
# st.write('name: {},auth_status: {}, username: {}'.format(name,authenticator.login('Login','main'),username))
if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    data = pd.read_csv('excel_check.csv')
    data.fillna('NULL',inplace = True)

    # Initialize Variables
    if "Brand_name" not in st.session_state:
        st.session_state["Brand_name"] = ""
    if "Region" not in st.session_state:
        st.session_state["Region"] = ""
    if "Market_Place" not in st.session_state:
        st.session_state["Market_Place"] = ""

    # Select the region ,'USA','Europe','Asia'
    region = st.multiselect(label='Select Region',
                        options=['India'], 
                        default = ['India'])
    # st.write('The options selected are:', region)
    st.session_state['Region'] = region

    # Select Market Places
    region_marketplace = {'India':['Amazon'],
                        'USA':['Amazon','shopify','Walmart'],
                        'Europe':['Amazon','shopify','Walmart'],
                        'Asia':['Amazon','shopify','Walmart']}
    available_marketplaces = list(set(np.ravel([region_marketplace[i] for i in ['USA','Europe']])))   
    marketplace = st.multiselect(label='Select Market Places',
                        options=available_marketplaces,
                        default = ['Amazon'])
    # st.write('The options selected are:', marketplace)
    st.session_state['Market_Place'] = marketplace

    # Select the Brand Name

    brand_name = st.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"])
    scrape_submit = st.button("Submit")

    pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
    # command = 'python AmazonSearchProductSpider\spiders\__init__.py'
    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    if scrape_submit:
        st.session_state["Brand_name"] = brand_name
        st.write("Scraping Started for {} ".format(brand_name))
        # cmd ='python AmazonSearchProductSpider/spiders/__init__.py'
        # os.system(cmd)
        import subprocess
        variable = 'Run_Spider.py'
        subprocess.call(f"{sys.executable} " + variable , shell=True)
        # result = subprocess.run(command.split(),stdout=subprocess.PIPE)
        df = pd.read_csv('DataStore/Scrapy_Res.csv')
        listing_cols = ['product_url','product_asin','product_brand','product_title','product_price','product_stars','product_images','product_bullets',
        'product_rating_count','country_of_origin','product_weight','product_material','product_category','item_height','item_length','item_width','aplus','description']
        df = df[listing_cols]
        # st.write(os.listdir('DataStore/'))
        if 'ScrapedData_pg_v1.csv' in os.listdir('DataStore/'):
            # st.write('TRUE')
            overall_data = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
        else:
            # st.write('FALSE')
            overall_data = pd.DataFrame(columns=listing_cols)
        overall_data = pd.concat([df,overall_data])
        st.write("Scraping Completed!!! ")
        overall_data.to_csv('DataStore/ScrapedData_pg_v1.csv',index=False)
        # view_df = st.button("View")
        # if view_df:
        st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
        st.dataframe(df)
        # st.write('QC Check on Data Fields Started .....')
        # df = pd.read_csv('DataStore/Scrapy_Res.csv')
        # df.fillna('NULL',inplace = True)
        # res_df = QC_check1(df[['product_brand','product_title','description','product_bullets']].copy())
        # st.write('QC Check on Data Fields Completed!!!')
        # display_res = st.button('Display')
        # if display_res:
        # st.dataframe(res_df)
        csv = convert_df(df)
        st.download_button(
            label="Download",
            data=csv,
            file_name='DataStore/QC_res_ScrapedData.csv',
            mime='text/csv',
        )
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
# Loading data

# data = pd.read_csv('excel_check.csv')
# data.fillna('NULL',inplace = True)

# # Initialize Variables
# if "Brand_name" not in st.session_state:
#     st.session_state["Brand_name"] = ""
# if "Region" not in st.session_state:
#     st.session_state["Region"] = ""
# if "Market_Place" not in st.session_state:
#     st.session_state["Market_Place"] = ""

# # Select the region ,'USA','Europe','Asia'
# region = st.multiselect(label='Select Region',
#                      options=['India'], 
#                      default = ['India'])
# # st.write('The options selected are:', region)
# st.session_state['Region'] = region

# # Select Market Places
# region_marketplace = {'India':['Amazon'],
#                       'USA':['Amazon','shopify','Walmart'],
#                       'Europe':['Amazon','shopify','Walmart'],
#                       'Asia':['Amazon','shopify','Walmart']}
# available_marketplaces = list(set(np.ravel([region_marketplace[i] for i in ['USA','Europe']])))   
# marketplace = st.multiselect(label='Select Market Places',
#                      options=available_marketplaces,
#                      default = ['Amazon'])
# # st.write('The options selected are:', marketplace)
# st.session_state['Market_Place'] = marketplace

# # Select the Brand Name

# brand_name = st.text_input("Search for a Brand Name (if multiple then seperate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"])
# submit = st.button("Submit")

# pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
# # command = 'python AmazonSearchProductSpider\spiders\__init__.py'
# if submit:
#     st.session_state["Brand_name"] = brand_name
#     st.write("Scraping Started for {} ".format(brand_name))
#     cmd ='python AmazonSearchProductSpider/spiders/__init__.py'
#     os.system(cmd)
#     # result = subprocess.run(command.split(),stdout=subprocess.PIPE)
#     df = pd.read_csv('DataStore/Scrapy_Res.csv')
#     listing_cols = ['product_url','product_asin','product_brand','product_title','product_price','product_stars','product_images','product_bullets',
#     'product_rating_count','country_of_origin','product_weight','product_material','product_category','item_height','item_length','item_width','aplus','description']
#     df = df[listing_cols]
#     # st.write(os.listdir('DataStore/'))
#     if 'ScrapedData_pg_v1.csv' in os.listdir('DataStore/'):
#         # st.write('TRUE')
#         overall_data = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
#     else:
#         # st.write('FALSE')
#         overall_data = pd.DataFrame(columns=listing_cols)
#     overall_data = pd.concat([df,overall_data])
#     st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
#     st.write('Overall Data Size is {}'.format(overall_data.shape))
#     overall_data.to_csv('DataStore/ScrapedData_pg_v1.csv',index=False)
#     st.dataframe(overall_data)
