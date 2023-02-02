import pandas as pd
import numpy as np
import os
import streamlit as st
import pickle as pkl
import pandas as pd
import subprocess
st.set_page_config(
    page_title="QCListing"
)

st.title("QCListing")
# st.sidebar.success("Select Action")

# Loading data

data = pd.read_csv('excel_check.csv')
special_char = pd.read_excel('Special characters list.xlsx',header=None)
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

brand_name = st.text_input("Search for a Brand Name(if multiple then seperate using ' , ') eg. Yellow Chimes", st.session_state["Brand_name"])
submit = st.button("Get")

pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
# command = 'python AmazonSearchProductSpider\spiders\__init__.py'
if submit:
    st.session_state["Brand_name"] = brand_name
    st.write("Scraping Started for {} ".format(brand_name))
    cmd ='python AmazonSearchProductSpider\spiders\__init__.py'
    os.system(cmd)
    # result = subprocess.run(command.split(),stdout=subprocess.PIPE)
df = pd.read_csv('DataStore/Scrapy_Res.csv')
overall_data = pd.read_parquet('ScrapedData_pg_v1.parquet')
overall_data = pd.concat([df,overall_data])
st.write('Overall Data Size is {}'.format(overall_data.shape))
overall_data.to_parquet('DataStore/ScrapedData_pg_v1.parquet',index=False)
st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
# st.dataframe(df)

