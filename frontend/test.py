import streamlit as st
print("Streamlit version:", st.__version__)
print("Query params:", st.query_params)
st._set_query_params(page="test")
print("New query params:", st.query_params)
