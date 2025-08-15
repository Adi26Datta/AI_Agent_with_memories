import streamlit as st
import textwrap

from functions.main import AgentToolCall
from functions.Memory.memory import load_and_save_long_term
from langchain_core.messages import HumanMessage, AIMessage

# Default thread
thread = "MyChatbot"

st.set_page_config(page_title="Napoleon Chatbot", page_icon="🤖")
st.title("Napoleon History")

# Sidebar for threads
thread_id = st.sidebar.text_input("Thread ID", value=thread)
print(f"Using thread ID: {thread_id}")
# Initialize session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.text_input("Your question:")

if st.button("Send") and user_input:
    # 1️⃣ Add user message locally
    st.session_state.messages.append(("user", user_input))
    print(f"st.session_state.messages: {st.session_state.messages}")
    # 2️⃣ Wrap history into LangChain message types
    wrapped_msgs = []
    for role, msg in st.session_state.messages:
        if role == "user":
            wrapped_msgs.append(HumanMessage(content=msg))
        elif role == "assistant":
            wrapped_msgs.append(AIMessage(content=msg))
    print(f"Wrapped message: {wrapped_msgs}")

    # 3️⃣ Save to Neo4j and fetch memories
    wrapped_state = {"thread_id": thread_id, "messages": wrapped_msgs}
    print(f"Wrapped state for agent: {wrapped_state}")
    agent_inputs = load_and_save_long_term(wrapped_state)
    print(f"Agent inputs after loading and saving long-term memory: {agent_inputs}")
    print("------------------------------------------------------------------------------------------------------------")
    # 4️⃣ Call the agent
    try:
        response = AgentToolCall.invoke(
            {"messages": agent_inputs, "thread_id": thread_id},
            {"configurable": {"thread_id": thread_id}}
        )
        print(f"Agent responsed")
        # FinalOutput is returned; access structured_response and its response attribute
        bot_reply = response['structured_response'].response
        print(f"Bot reply: {bot_reply}")
        print("------------------------------------------------------------------------------------------------------------")
    except Exception as e:
        st.error(f"⚠️ Agent error: {e}")
        bot_reply = None

    # 5️⃣ Store assistant reply locally
    if bot_reply:
        st.session_state.messages.append(("assistant", bot_reply))

# Render chat history
for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    elif role == "assistant":
        st.markdown(f"**Bot:** {textwrap.fill(msg, width=60)}")
