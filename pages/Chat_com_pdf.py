import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message
from utils import get_chain, get_similar_docs, get_answer
from utils import create_docs, split_docs, get_embeddings, get_vectorstore
from langchain.chains.conversation.memory import ConversationSummaryMemory
load_dotenv()

if 'chain' not in st.session_state:
    st.session_state['chain'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'API_KEY' not in st.session_state:
    st.session_state['API_KEY'] =''
if 'db' not in st.session_state:
    st.session_state['db'] = None
if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] =''
st.session_state['API_KEY'] =  os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Cicero - Assistente Documental da PCA", page_icon=":robot_face:")
st.header("Faça o upload dos documentos pdf 📄")
pdfs_uploaded = st.file_uploader("Carregue os seus PDFs aqui e clica em 'Processar'", accept_multiple_files=True, type=["pdf"])
if st.button("Processar"):
    with st.spinner("Processando..."):    
        st.session_state['unique_id'] = uuid.uuid4().hex
        # get pdf text
        docs = create_docs(pdfs_uploaded, st.session_state['unique_id'] )
        st.success("Documentos carregados✅")

        # get the text chunks
        chunks = split_docs(docs)
        st.success("Chunks criados✅")

        # embeddings
        embeddings = get_embeddings(st.session_state['API_KEY'])
        st.success("Embedding criados✅")
        
        # create vectorstore
        db = get_vectorstore(chunks, embeddings)
        st.session_state['db'] = db
        st.success("Vector Store criado✅")
        
        # create conversation chain
        st.session_state['chain'] = get_chain(st.session_state['API_KEY'])
        st.success("Chain criado✅")


response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        question = st.text_area(label="Digite a sua pergunta:",key='question_input', height=100)
        submit_button = st.form_submit_button(label='Enviar')

        if submit_button:
            st.session_state['chat_history'].append(question)
            relevant_docs = get_similar_docs(db=st.session_state['db'], query=question, k=1)
            print(f"{'='*200}\nDocumentos Base da resposta:{relevant_docs}")
            answer = get_answer(chain=st.session_state['chain'],query=question, relevant_docs=relevant_docs)
            st.session_state['chat_history'].append(answer)

            with response_container:
                for i in range(len(st.session_state['chat_history'])):
                        if (i % 2) == 0:
                            message(st.session_state['chat_history'][i], is_user=True, key=str(i) + '_user')
                        else:
                            message(st.session_state['chat_history'][i], key=str(i) + '_AI')
        
    