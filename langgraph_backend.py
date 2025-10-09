from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage
#from langgraph.checkpoint.memory import InMemorySaver   #previous to database
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from typing_extensions import Annotated
import sqlite3

load_dotenv()
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
class ChatState(TypedDict):
    #add on messages
    messages:Annotated[list[BaseMessage],add_messages]

def start_chat(state:ChatState) -> ChatState:
    message=state['messages']
    response=llm.invoke(message)
    return {'messages':state['messages'] + [response]}
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "cahtbot.db")
connection = sqlite3.connect(DB_PATH, check_same_thread=False)
 #database creation
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
def retrieve_all_threads():    #this tells us number of unique threads in the program
    """Retrieve all unique thread IDs from LangGraph checkpoints."""
    all_threads = set()
    
    try:
        for item in check_pointer.list(None):
            if isinstance(item, tuple) and len(item) >= 2:
                metadata = item[1]
                thread_id = metadata.get("configurable", {}).get("thread_id")
                if thread_id:
                    all_threads.add(thread_id)
    except Exception as e:
        print("Error reading checkpoints:", e)
    
    return list(all_threads)


def save_thread_name(thread_id, thread_name):
    """Store or update a chat's name in the same SQLite DB."""
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_names (
            thread_id TEXT PRIMARY KEY,
            thread_name TEXT
        )
    """)
    cur.execute("""
        INSERT INTO chat_names (thread_id, thread_name)
        VALUES (?, ?)
        ON CONFLICT(thread_id) DO UPDATE SET thread_name = excluded.thread_name
    """, (str(thread_id), thread_name))
    connection.commit()


def retrieve_thread_names():
    """Load all saved chat names as {thread_id: thread_name}."""
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_names (
            thread_id TEXT PRIMARY KEY,
            thread_name TEXT
        )
    """)
    cur.execute("SELECT thread_id, thread_name FROM chat_names")
    data = cur.fetchall()
    return {row[0]: row[1] for row in data}




