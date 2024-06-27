import pandas as pd
import streamlit as st

####################################################
#                      PARAMS                      #
####################################################
st.set_page_config(page_title="Intro", page_icon="👋",)


####################################################
#                      APP                         #
####################################################
st.write("# Welcome to Creative Fiancing Calculator App! 👋")

st.sidebar.success("Select a calculator.")

st.markdown(
    """
    The leads app is built specifically for
    calculating creative financing strategies.
    **👈 Select a creative financing type from the sidebar** to calculate
    the offer terms for a deal!
    ### Want to learn more?
    - Check out [OfferREI](https://www.offerrei.com/index.html?fpr=techinrealestate) to auto create offers
"""
)