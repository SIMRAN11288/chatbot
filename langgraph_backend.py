from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage
#from langgraph.checkpoint.memory import InMemorySaver   #previous to datab

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from typing_extensions import Annotated
import sqlite3

load_dotenv()
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
class ChatState(TypedDict):
    #add on messages
    messages:Annotated[list[BaseMessage],add_messages]
    thread_name:str

def start_chat(state:ChatState) -> ChatState:
    message=state['messages']
    response=llm.invoke(message)
    return {'messages':state['messages'] + [response]}
connection= sqlite3.connect(database='cahtbot.db',check_same_thread=False)  #database creation
check_pointer=SqliteSaver(conn=connection)
graph=StateGraph(ChatState)

graph.add_node("start_chat",start_chat)
graph.add_edge(START,"start_chat")
graph.add_edge("start_chat",END)

chatbot=graph.compile(checkpointer=check_pointer)
# thread=chatbot.get_state("user123")
# chatbot.update_state("user123",{"messages":[])
# thread_ID='user123'

# while True:
#     User_input=input("enter your query")
#     print("USER:",User_input)
#     if User_input.strip().lower() in ['end','quit','stop']:
#         break
#     config={"configurable":{"thread_id":thread_ID}}
#     response=chatbot.invoke({"messages":[HumanMessage(content=User_input)]},config=config)
#     print("AI:", response['messages'][-1].content)
    
    #for database code
def retrieve_all_threads():    # this si to tell number of unique threads in the code
    all_threads = set()
    for _, metadata, _ in check_pointer.list(None):
        all_threads.add(metadata["configurable"]["thread_id"])
    return list(all_threads)

    
def save_thread_name(thread_id, thread_name, messages=None):
    if messages is None:
        messages = []
    
    state = {
        "messages": messages,
        "thread_name": thread_name
    }
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "thread_name": thread_name
        }
    }
    
    metadata = {
        "configurable": {
            "thread_id": thread_id,
            "thread_name": thread_name
        }
    }
    
    # ✅ Correct argument order for SqliteSaver.put()
    # put(config, checkpoint, metadata, new_versions)
    check_pointer.put(config, state, metadata, {})

def retrieve_thread_names():
    thread_names = {}
    for checkpoint, metadata, versions in check_pointer.list(None):
        thread_id = metadata["configurable"]["thread_id"]

        if isinstance(checkpoint, dict):
            thread_name = checkpoint.get("thread_name", str(thread_id)[:8])
        else:
            thread_name = str(thread_id)[:8]

        thread_names[thread_id] = thread_name

    return thread_names

















