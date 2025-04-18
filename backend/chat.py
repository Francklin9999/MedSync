from dotenv import load_dotenv
import os
import json

from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import AgentExecutor
from google.generativeai.types import HarmCategory, HarmBlockThreshold


load_dotenv()

def connect_to_vstore():
    embeddings = HuggingFaceEmbeddings()
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name="Doc",
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace="MedDocs",
    )
    return vstore

def query_database(query, k=1):
    vstore = connect_to_vstore()

    retriever = vstore.as_retriever(search_kwargs={"k": k})

    retrieved_data = retriever.get_relevant_documents(query)

    context = "\n".join([doc.page_content for doc in retrieved_data])

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt_template = ( 
        "You are a helpful assistant answering medical questions based on the provided context. "
        "Answer the query using the context information.\n"
        "Make sure your awnser responde to the user question"
        "Query: {query}\n"
        "Context: {context}" 
    )

    result = llm.invoke(prompt_template.format(query=query, context=context))

    return result

def query_database(query, k=1):
    vstore = connect_to_vstore()

    retriever = vstore.as_retriever(search_kwargs={"k": k})

    retriever_tool = create_retriever_tool(
    retriever,
    "MedDocs",
    "Search for information about medical issues. For any questions about medical issues, you must use this tool!",
    )

    # context = "\n".join([doc.page_content for doc in retrieved_data])

    prompt = hub.pull("hwchase17/openai-functions-agent")
    
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=1,
        safety_settings=safety_settings
    )

    tools = [retriever_tool]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": query})

    output = response.get('output', '')

    return output

def add_documents_to_vstore(documents):
    try:
        vstore = connect_to_vstore()

        for doc_id, doc_text in documents.items():
            document = Document(
                id=doc_id,
                page_content=doc_text, 
            )

            vstore.add_documents([document]) 
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    # with open("sections.json", "r") as file:
    #     documents = json.load(file)

    # add_documents_to_vstore(documents)

    print(query_database("Cure"))
    # print(query_database("Best Cure Headache"))

if __name__ == "__main__":
    main()