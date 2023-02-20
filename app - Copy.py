import subprocess
import streamlit as st
import pandas as pd
# Define the Scrapy command to run the spider
command = " scrapy crawl amazon_search_product -o brand_items_st.csv "

# Call the command using subprocess

# Display the output of the Scrapy command in Streamlit
#input_value = st.text_input("Enter your input:")

# Add a submit button
if st.button("Scrape"):
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)

    # Write the input value to the app
    #st.write(result.stdout.decode())
    df =pd.read_csv("brand_items_st.csv")
    st.write("CSV data:", df)
   