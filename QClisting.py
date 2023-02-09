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
import excel_checks
from datetime import datetime
from send_email import send_email

st.set_page_config(
    page_title="Listing QC"
)

st.title("Listing QC")
# st.sidebar.success("Select Action")


data = pd.read_csv('excel_check.csv')
data.fillna('NULL',inplace = True)

# Initialize Variables
if "r_email" not in st.session_state:
    st.session_state["r_email"] = ""
if "Brand_name" not in st.session_state:
    st.session_state["Brand_name"] = ""
if "Region" not in st.session_state:
    st.session_state["Region"] = ""
if "Market_Place" not in st.session_state:
    st.session_state["Market_Place"] = ""

# Enter email to send the results on 
email_place = st.empty()
r_email = email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"])

# Select the region ,'USA','Europe','Asia'
region_place = st.empty()
region = region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'])
# st.write('The options selected are:', region)
st.session_state['Region'] = region

# Select Market Places
marketplace_place = st.empty()
region_marketplace = {'India':['Amazon'],
                    'USA':['Amazon','shopify','Walmart'],
                    'Europe':['Amazon','shopify','Walmart'],
                    'Asia':['Amazon','shopify','Walmart']}
available_marketplaces = list(set(np.ravel([region_marketplace[i] for i in ['USA','Europe']])))   
marketplace = marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled=False)
# st.write('The options selected are:', marketplace)
st.session_state['Market_Place'] = marketplace

# Select the Brand Name
brandname_place = st.empty()
brand_name = brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"])
submitplace = st.empty()
submit = submitplace.button("Submit",disabled=False,key='submit1')
stop = st.button('Stop')
pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

if not stop and submit:
    submitplace.button("Submit",disabled=True,key='submit2')
    email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"],disabled=True,key = 'emailplace')
    region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'],disabled = True,key = 'regionplace')
    marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled = True,key = 'marketplace')
    brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"],disabled = True,key = 'brandplace')

    st.session_state["Brand_name"] = brand_name
    st.write('The Scraping+Listing QC Checks are in process. PLEASE DO NOT CLOSE THE TAB')
    textplace = st.empty()
    textplace.write("Scraping Started for {} ".format(brand_name))
    import subprocess
    variable = 'Run_Spider.py'
    subprocess.call(f"{sys.executable} " + variable, shell=True)
    try:
        df = pd.read_csv('DataStore/Scrapy_Res.csv')
        df['product_brand'] = df['product_brand'].apply(lambda x:st.session_state['Brand_name'].title() if x=='NA' else x).copy()
    except:
        df = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
    listing_cols = ['product_url','product_asin','product_brand','product_title','product_price','product_stars','product_images','product_bullets',
    'product_rating_count','country_of_origin','product_weight','product_material','product_category','item_height','item_length','item_width','aplus','description']
    df = df[listing_cols]

    # st.dataframe(df['product_brand'])
    textplace.write('Scraping Complete!!!')
    st.write('Estimated time for completion is about {} hours'.format(str(round(len(df)*10/60,1)) if (len(df)*10)/60 >1 else str(len(df)*10)))
    # st.write(os.listdir('DataStore/'))
    st.write('QC_Checks Started')
    df.fillna('NA',inplace = True)
    res_df = excel_checks.QC_check1(df)
    res_df = res_df.drop(['product_weight','product_material','product_category','item_height','item_length','item_width'], axis = 1)
    st.write('QC Checks Completed!!!')
    submitplace.button("Submit",disabled=False,key='submit3')
    email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"],disabled=False,key = 'emailplace3')
    region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'],disabled = False,key = 'regionplace3')
    marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled = False,key = 'marketplace3')
    brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"],disabled = False,key = 'brandplace3')
    st.dataframe(res_df)
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    filename = 'Listing_QC_results_'+st.session_state['Brand_name']+'_'+dt_string+'.csv'
    res_df.to_csv('DataStore/'+filename ,index = False)
    if len(r_email)>0:
        send_email(r_email,filename)

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
    csv = convert_df(res_df)
    st.download_button(
        label="Download",
        data=csv,
        file_name='DataStore/'+st.session_state['Brand_name']+'_res.csv',
        mime='text/csv',
    )