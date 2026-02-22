from dotenv import load_dotenv
import os
from src.helper import download_hugging_face_embeddings, load_pdf_files, filter_to_minimal_docs, text_split
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore


load_dotenv()

PINE_CONE_API_KEY = os.getenv("PINECONE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

os.environ["PINECONE_API_KEY"] = PINE_CONE_API_KEY
os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY

extracted_data = load_pdf_files("data")
filter_data = filter_to_minimal_docs(extracted_data)
texts_chunk = text_split(filter_data)

embeddings = download_hugging_face_embeddings()
pinecone_api_key = PINE_CONE_API_KEY
pc = Pinecone(api_key=pinecone_api_key)

index_name = "medical-chatbot"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,  # Dimension of the embeddings
        metric="cosine",  # Similarity metric
        spec=ServerlessSpec(cloud = "aws", region = "us-east-1")  # Serverless configuration
    )
index = pc.Index(index_name)

docsearch = PineconeVectorStore.from_documents(
    documents=texts_chunk,
    embedding=embeddings,
    index_name=index_name
)