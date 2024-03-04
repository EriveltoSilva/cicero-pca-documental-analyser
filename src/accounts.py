import firebase_admin
import streamlit as st
from firebase_admin import auth
from firebase_admin import credentials

cred = credentials.Certificate("./db/cicero-pca-c5e49bd1adba.json")
# firebase_admin.initialize_app(cred)

def app():
    st.title("Bem Vindo ao :blue[Cicero], o Seu assistente Virtual Favorito🤖")
    choice = st.selectbox("Login/Criar conta", ['Login', 'Sign Up'])
    if choice == 'Login':
        email = st.text_input('Seu endereço de Email')
        password = st.text_input("Sua password", type='password')
        st.button('Entrar')

    elif choice=='Sign Up':
        username = st.text_input('Seu username')
        email = st.text_input('Seu endereço de Email')
        password = st.text_input("Sua password", type='password')
        confirmation_password = st.text_input("Sua password de confirmação", type='password')
        if st.button('Criar conta'):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success("Conta criada com sucesso!")
            st.markdown("Faça login usando as credencias criadas!")
            st.balloons("")

