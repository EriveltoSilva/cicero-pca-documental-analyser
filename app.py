import firebase_admin
import streamlit as st
from firebase_admin import auth
from firebase_admin import credentials

cred = credentials.Certificate("")
firebase_admin.initialize_app(cred)


st.title("Bem Vindo ao Cicero, o Seu assistente Virtual Favorito🤖")
choice = st.selectbox("Login/Signup", ['Login', 'Sign Up'])
if choice == 'Login':
    email = st.text_input('Endereço de Email')
    password = st.text_input("Password", type='password')
    st.button('Login')

else:
    ...