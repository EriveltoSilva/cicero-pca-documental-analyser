import os
import asyncio
# import pinecone
# from langchain import OpenAI
# from langchain_community.llms import OpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAI,OpenAIEmbeddings

# from langchain.document_loaders import PyPDFDirectoryLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY=str(os.getenv('OPENAI_API_KEY'))
directory = 'Docs/'

# Load Documents
def load_docs(directory="Docs/"):
    loader = PyPDFDirectoryLoader(directory)
    documents = loader.load()
    return documents

# Transform(Split) Documents
def split_docs(documents, chunk_size=2000, chunk_overlap=250):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n", "\n\n","\n\n\n"], chunk_size=chunk_size, chunk_overlap=chunk_overlap) # Break large documents in few chunks
    docs = text_splitter.split_documents(documents=documents)
    return docs

def get_embeddings():
    return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def get_vector_db(documents, embeddings):
    return Chroma.from_documents(documents=documents, embedding=embeddings)

def get_similar_docs(db, query, k=2):
    return db.similarity_search(query, k=k)

# async def get_answer(chain,query, relevant_docs):
def get_answer(chain,query, relevant_docs):
#   response = chain.run(input_documents=relevant_docs, question=query)
    response = chain.invoke({"input_documents":relevant_docs, "question":query}, return_only_outputs=True)["output_text"]
    # print(chain.memory.buffer)
    return response

def get_chain():
    template = """Você é um educado e alegre chatbot da empresa InovAI Soluções. Seu nome é Ino. Use as seguintes partes do contexto para responder à pergunta no final. Responda de modo amigavel e usando muitos emojis em cada resposta. Se você não sabe a resposta, apenas diga que não sabe e peça que o cliente entre em contacto com o número de telefone fornecido no contexto, ou pelo email da empresa, não tente inventar uma resposta.Use no máximo três frases e mantenha a resposta o mais concisa possível. Se fizerem uma pergunta que não tenha relação com a InovAI, seus serviços e etc responda cordialmente que só respondes perguntas relacionadas a InovAI. Não responda a perguntas relacionadas a preços de serviços, peça cordialmente para entrar em contacto directo com a InovAI para obter detalhes de precificação.Responda cada pergunta na primeira pessoa do plural como se tú fosses um Funcionário da empresa. Peça sempre primeiro o nome do cliente e Use o nome do cliente ao responder as perguntas. Após cada resposta pergunte sempre se deseja saber mais alguma coisa.
        {context}
        {chat_history}
        Questão: {question}
        Resposta útil:
    """
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "chat_history", "question"], 
        template=template
    )


    return load_qa_chain(
        llm=OpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-instruct"), 
        chain_type="stuff",
        memory=ConversationBufferMemory(memory_key="chat_history", input_key="question"), 
        prompt=QA_CHAIN_PROMPT
    )



if __name__== '__main__':
    documents = load_docs(directory)
    print(f"Num docs(pages):{len(documents)}")

    docs = split_docs(documents)
    embeddings = get_embeddings()
    db = get_vector_db(documents=docs, embeddings=embeddings)
    # Se a pessoa te saudar saude de volta e pergunte o nome

    chain = get_chain()

    try:
        while True:
            our_query = input("O que deseja saber:")
            if our_query.lower() == 'exit':
                raise KeyboardInterrupt("saindo")
            
            relevant_docs = get_similar_docs(db=db, query=our_query)
            # print(f"Documentos Base da resposta:{relevant_docs}")
            answer = get_answer(chain=chain,query=our_query, relevant_docs=relevant_docs)
            print(answer)
            # print(f"Resposta:{answer}")
    except KeyboardInterrupt:
        print("\n\n")
        print("Saindo e finalizando o programa!")

