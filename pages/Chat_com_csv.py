import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from dotenv import load_dotenv
load_dotenv()

query=""
button = None

def query_agent(data, query):
    df = pd.read_csv(data)
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    return agent.run(query)


st.title("Pronto para analisar alguns cvs📝")
st.header("Carregue o seu ficheiro csv⬇️:")
          
data = st.file_uploader("Carregamento do Ficheiro", type="csv")
if data:
    st.success("Arquivo carregado com successo")
    query = st.text_area("Digite a sua pergunta")
    button = st.button("Enviar Pergunta")

if button:
    if not data:
        st.error("Erro.Não foi carregado nenhum arquivo.")
    
    else:
        answer = query_agent(data=data, query=query)
        st.write(answer)