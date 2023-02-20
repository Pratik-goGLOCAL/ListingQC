from send_mail import SendMail
import streamlit as st
import os

if st.session_state['asin_brand']=='ASIN':
    resfor = 'ASIN'
    names = st.session_state['ASIN']
else:
    resfor = st.session_state['Brand_name']
    names = st.session_state['Brand_name']
def send_email(r_email,filename):
    # Create SendMail object
    new_mail = SendMail(
        # List (or string if single recipient) of the email addresses of the recipients
        [r_email], 
        # Subject of the email
        'Listing QC Results for '+resfor,
        # Body of the email
        '''Hello,

        The Listing QC check for {} is sucessfully completed!!!
        The results are attached with this mail.
        
        Thanks'''.format(names), 
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