import os
import uuid
import pandas as pd
import streamlit as st
from streamlit_chat import message
from langchain_openai import ChatOpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from dotenv import load_dotenv

def app():
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    message_history = ChatMessageHistory()

    question=""
    button = None
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'agent' not in st.session_state:
        st.session_state['agent'] = None
    if 'unique_id' not in st.session_state:
        st.session_state['unique_id'] = ""



    def create_agent(data) -> AgentExecutor:
        df = pd.read_csv(data)
        agent = create_pandas_dataframe_agent(
            ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,model="gpt-3.5-turbo-0613"),
            df, 
            verbose=False, 
            agent_type=AgentType.OPENAI_FUNCTIONS 
        )
        return agent

    def query_agent(query, agent):
        try:
            if st.session_state['chat_history']:
                response = agent.invoke({"chat_history": st.session_state['chat_history'],"input":query,})
            else:
                response = agent.invoke({"input":query, "chat_history": st.session_state['chat_history'],})
            print(response)
            response = response['output']
        except ValueError as e:
            print("ValueErro#"*100)
            print(e)
            response = "Não achei nenhuma resposta satisfatória para esse pergunta. Reformule ela por favor"
        except Exception as e:
            print("Exception#"*100)
            print(e)
            response = "Não achei nenhuma resposta satisfatória para esse pergunta. Reformule ela por favor"
        finally:
            st.session_state['chat_history'].append(HumanMessage(query),)
            st.session_state['chat_history'].append(AIMessage(response),)
            return response



    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in st.session_state:
            st.session_state[session_id] = ChatMessageHistory()
        return st.session_state[session_id]


    def create_agent_with_memory(data):
        agent_with_chat_history = RunnableWithMessageHistory(
        create_agent(data),
        # get_session_history,
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        )
        return agent_with_chat_history
    def query_agent_with_memory(query, session_id, agent):
        response = agent.invoke(
            {"input": query},
            config={"configurable": {"session_id": "<foo>"}},
        )
        return response




    st.title("Pronto para analisar alguns csv📝")
    data = st.file_uploader("Carregamento do Ficheiro", type="csv")
    if data:
        st.session_state['unique_id'] = uuid.uuid4().hex
        st.session_state['agent'] = create_agent(data)
        st.success("Arquivo carregado com successo")

        response_container = st.container()
        container = st.container()

        with container:
            question = st.chat_input("Digite a sua pergunta")
            if question:
                with response_container:
                    answer = query_agent(question,st.session_state['agent'])
                    for i in range(len(st.session_state['chat_history'])):
                        if (i % 2) == 0:
                            with st.chat_message("user"):
                                st.write(st.session_state['chat_history'][i].content)
                        else:
                            with st.chat_message("assistant"):
                                st.write(st.session_state['chat_history'][i].content)

                    