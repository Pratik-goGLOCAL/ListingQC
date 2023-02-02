import pandas as pd
import numpy as np
import os
import streamlit as st
import pickle as pkl
import pandas as pd
import subprocess
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="ListingQC"
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
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name,authentication_status,username = authenticator.login('Login','main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state["name"]}*')
    # st.title('Some content')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

# Loading data

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

brand_name = st.text_input("Search for a Brand Name (if multiple then seperate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"])
submit = st.button("Submit")

pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
# command = 'python AmazonSearchProductSpider\spiders\__init__.py'
if submit:
    st.session_state["Brand_name"] = brand_name
    st.write("Scraping Started for {} ".format(brand_name))
    cmd ='python AmazonSearchProductSpider/spiders/__init__.py'
    os.system(cmd)
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
    st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
    st.write('Overall Data Size is {}'.format(overall_data.shape))
    overall_data.to_csv('DataStore/ScrapedData_pg_v1.csv',index=False)
    st.dataframe(overall_data)
