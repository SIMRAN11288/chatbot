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
def retrieve_all_threads():  #this tells us number of unique threads in the program
    all_threads=set()
    for checkpoint in check_pointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)
    
def save_thread_name(thread_id, thread_name, messages=None):
    if messages is None:
        messages = []
    check_pointer.put(
        {"messages": messages,
        "thread_name": thread_name
        },
        config={"configurable": {"thread_id": thread_id}}
    )

def retrieve_thread_names():
    thread_names = {}
    for checkpoint in check_pointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        # ✅ retrieve from state values
        thread_name = checkpoint.state if hasattr(checkpoint,"state") else checkpoint.value
        thread_name = state.get("thread_name", str(thread_id)[:8])
        thread_names[thread_id] = thread_name
    return thread_names
        









