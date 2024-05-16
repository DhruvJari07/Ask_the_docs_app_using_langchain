from langchain_community.llms import HuggingFaceHub
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
import streamlit as st

load_dotenv()
Huggingface_api = os.getenv("Huggingface_api")


def generate_response(uploaded_file, query_text):
    # Load document if file is uploaded

    if uploaded_file is not None:
        documents = [uploaded_file.read().decode()]
        # Split documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.create_documents(documents)
        # Select embeddings
        repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
        llm = HuggingFaceHub(repo_id=repo_id, huggingfacehub_api_token=Huggingface_api)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Create a vectorstore from documents
        db = Chroma.from_documents(texts, embeddings)
        # Create retriever interface
        retriever = db.as_retriever()
        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
        return qa.invoke(query_text)['result'].split(":")[-1]

# Page title
st.set_page_config(page_title='🦜🔗 Ask the Doc App')
st.title('🦜🔗 Ask the Doc App')

# File upload
uploaded_file = st.file_uploader('Upload an article', type='txt')
# Query text
query_text = st.text_input('Enter your question:', placeholder = 'Ask a question from the document.', disabled=not uploaded_file)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit', disabled=not(uploaded_file and query_text))
    if submitted:
        with st.spinner('Searching...'):
            response = generate_response(uploaded_file, query_text)
            result.append(response)
            

if len(result):
    st.info(response)
    