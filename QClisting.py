import pandas as pd
import numpy as np
import os
import streamlit as st
import pickle as pkl

import subprocess

import json
import scrapy
from scrapy.crawler import CrawlerProcess,CrawlerRunner
from urllib.parse import urljoin
import re
import sys
sys.path.append('/QClisting')
from loguru import  logger



st.set_page_config(
    page_title="Listing QC"
)

st.title("Listing QC")
# st.sidebar.success("Select Action")


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
submit = st.button("Submit")

pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# command = 'python AmazonSearchProductSpider\spiders\__init__.py'
if submit:
    st.session_state["Brand_name"] = brand_name
    st.write("Scraping Started for {} ".format(brand_name))
    # cmd ='python AmazonSearchProductSpider/spiders/__init__.py'
    # os.system(cmd)
    import subprocess
    variable = 'Run_Spider.py'
    subprocess.call(f"{sys.executable} " + variable, shell=True)
    # cmd ='python Run_Spider.py'
    # os.system(cmd)
    # from Run_Spider import run_spider
    # run_spider()
    # result = subprocess.run(command.split(),stdout=subprocess.PIPE)
    try:
        df = pd.read_csv('DataStore/Scrapy_Res.csv')
    except:
        df = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
    listing_cols = ['product_url','product_asin','product_brand','product_title','product_price','product_stars','product_images','product_bullets',
    'product_rating_count','country_of_origin','product_weight','product_material','product_category','item_height','item_length','item_width','aplus','description']
    df = df[listing_cols]
    st.dataframe(df)
    st.write('Scraping Complete!!!')
    # st.write(os.listdir('DataStore/'))
    if 'ScrapedData_pg_v1.csv' in os.listdir('DataStore/'):
        # st.write('TRUE')
        overall_data = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
    else:
        # st.write('FALSE')
        overall_data = pd.DataFrame(columns=listing_cols)
    overall_data_new = pd.concat([df,overall_data])
    # st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
    # st.write('Overall Data Size is {}'.format(overall_data_new.shape))
    overall_data_new.to_csv('DataStore/ScrapedData_pg_v1.csv',index=False)
    csv = convert_df(df)
    st.download_button(
        label="Download",
        data=csv,
        file_name='DataStore/'+st.session_state['Brand_name']+'_res.csv',
        mime='text/csv',
    )
    # st.dataframe(overall_data_new)