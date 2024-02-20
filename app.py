import os
import streamlit as st
from streamlit_chat import message
from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
from dotenv import load_dotenv
load_dotenv()


def get_response(question, api_key):
    if st.session_state['conversation'] is None:
        llm = OpenAI(
            temperature=0,
            openai_api_key=api_key,
            model_name='gpt-3.5-turbo-instruct'
            )

        st.session_state['conversation'] = ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationSummaryMemory(llm=llm)
        )

    response=st.session_state['conversation'].predict(input=question)
    print(st.session_state['conversation'].memory.buffer)
    return response


if 'conversation' not in st.session_state:
    st.session_state['conversation'] =None
if 'messages' not in st.session_state:
    st.session_state['messages'] =[]
if 'API_KEY' not in st.session_state:
    st.session_state['API_KEY'] =''


# st.set_page_config(page_title="Chat GPT Clone", page_icon=":robot_face:")
st.set_page_config(page_title="Cicero - Assistente Documental da PCA", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>Como posso ajuda-lo hoje? </h1>", unsafe_allow_html=True)

if "sessionMessages" not in st.session_state:
    st.session_state.sessionMessages = []


st.sidebar.title("😎")
st.session_state['API_KEY'] =  os.getenv("OPENAI_API_KEY")
st.sidebar.write("Resumo de conversa")
summarise_button = st.sidebar.button("Resumir Conversa", key="btn_summarise")
if summarise_button:
    if st.session_state['conversation']:
        st.sidebar.write("Nice chatting with you my friend ❤️:\n\n"+st.session_state['conversation'].memory.buffer)
    else:
        st.sidebar.error("Não há conversa ainda para resumir")



response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        question = st.text_area(label="Digite a sua pergunta:",key='question_input', height=100)
        submit_button = st.form_submit_button(label='Enviar')

        if submit_button:
            st.session_state['messages'].append(question)
            response = get_response(question, st.session_state['API_KEY'])
            st.session_state['messages'].append(response)
            
            with response_container:
                for i in range(len(st.session_state['messages'])):
                        if (i % 2) == 0:
                            message(st.session_state['messages'][i], is_user=True, key=str(i) + '_user')
                        else:
                            message(st.session_state['messages'][i], key=str(i) + '_AI')
        
             

        
