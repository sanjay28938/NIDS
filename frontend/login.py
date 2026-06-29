import streamlit as st

def login():

    st.title("🔐 SOC Security Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "admin" and password == "cyber123":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid Credentials")