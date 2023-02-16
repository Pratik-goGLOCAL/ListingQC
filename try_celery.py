from celery import Celery
import streamlit as st
import time


st.set_page_config(
    page_title="Celery"
)

st.title("Celery")
app = Celery('try_celery', broker='pyamqp://guest@localhost//')

time.sleep(1000)


@app.task
def add(x, y):
    return x + y