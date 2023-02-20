from send_mail import SendMail
import streamlit as st
import os
from loguru import logger
import pickle

with open('DataStore/keyword_list.pickle', 'rb') as handle:
    keyword_list = pickle.load(handle)

resfor = list(keyword_list.keys())[0]
names = list(keyword_list.values())[0]
subject_for_email = 'Listing QC Results for '+resfor
body_for_email = '''Hello,

        The Listing QC check for {} is sucessfully completed!!!
        The results are attached with this mail.
        
        Thanks'''.format(names)
logger.info(subject_for_email)
logger.info(body_for_email)
def send_email(r_email,filename):
    # Create SendMail object
    new_mail = SendMail(
        # List (or string if single recipient) of the email addresses of the recipients
        [r_email], 
        # Subject of the email
        subject_for_email,
        # Body of the email
        body_for_email, 
        # Email address of the sender
        # Leave this paramter out if using environment variable 'EMAIL_ADDRESS'
        'pratik.g@goglocal.com' 
    )

    # If using HTML file
    # new_mail.add_html_file('/path/to/your/html/file')

    # List (or string if attaching single file) of relative or absolute file path(s) to files
    new_mail.attach_files(['DataStore/'+filename])

    # Print SendMail object to confirm email
    print(new_mail)

    # Send the email
    # Leave this parameter out if using environment variable 'EMAIL_PASSWORD'
    new_mail.send('sdqymwrluxqcytnx')
    os.remove('DataStore/'+filename)
    st.write('Resuls successfully sent to your email address!!!')