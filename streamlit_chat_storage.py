from langchain_core.messages import HumanMessage,AIMessage
from langgraph_backend import chatbot,retrieve_all_threads
import streamlit as st
import uuid
#------------------------utility functions--------------------------------------
def generate_new_ID():
    thread_ID=uuid.uuid4()
    return thread_ID

def reset_chat():
    # thread_ID=generate_new_ID()
    # st.session_state['thread_ID']=thread_ID
    # add_thread(st.session_state['thread_ID'])
    # reset_thread_name(thread_ID)
    # st.session_state['messages']=[ ]
    
    thread_ID = generate_new_ID()
    st.session_state['thread_ID'] = thread_ID
    add_thread(thread_ID)
    st.session_state['name_thread'][thread_ID] = f"Chat {len(st.session_state['chat_thread'])}"
    st.session_state['messages'] = []
    
def add_thread(thread_ID):
    if thread_ID not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_ID)
    
def load_conversation(thread_ID):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_ID}})
    return state.values.get('messages', [])
def reset_thread_name(thread_ID):
    st.session_state['name_thread'][thread_ID]=[]
#------------------------------new session------------------------------------
if 'messages' not in st.session_state:
    st.session_state['messages']=[]

if 'thread_ID' not in st.session_state:
    st.session_state['thread_ID']=generate_new_ID()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread']=retrieve_all_threads()   #provides a list of unique 
                                                                   #threads
add_thread(st.session_state['thread_ID'])

if 'name_thread' not in st.session_state:
    st.session_state['name_thread']={}
#--------------------------side bars------------------------------------------

st.sidebar.title('LangGraph History Con')
if st.sidebar.button('NEW CHAT'):
    reset_chat()
    st.rerun()
    
st.sidebar.header('My Converesations')

for thread_ID in st.session_state['chat_thread'][::-1]:
    thread_name = st.session_state['name_thread'].get(thread_ID, str(thread_ID)[:8])


    if st.sidebar.button(thread_name,key=f"btn_{str(thread_ID)}"):    #button expects a string
        st.session_state['thread_ID']=thread_ID
        messages=load_conversation(thread_ID)
        
        temp_messages=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role':role,'content':msg.content})
        st.session_state['messages']=temp_messages
        
active_session=st.session_state['thread_ID']
default_value=st.session_state['name_thread'].get(active_session,str(active_session)[:8])

name_thread=st.text_input("Give a name to this convo",
        value=default_value,
    key=f"name_{active_session}"
   )
st.session_state['name_thread'][active_session] = name_thread

#---------------invoke---------------------------

for messages in st.session_state['messages']:
    with st.chat_message(messages['role']):
        st.text(messages['content'])
        

user_input=st.text_input('Enter your query',key=f"user-input{str(st.session_state['thread_ID'])}")
if user_input:
    st.session_state['messages'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_ID']}}
    
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            (message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages":[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ))
        )
        
    st.session_state['messages'].append({'role':'assistant','content':ai_message})



