import streamlit as st
import os
from openai import OpenAI

# ---------------------------
# OpenAI Client (SAFE)
# ---------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Study Chatbot", layout="centered")
st.title("AI Study Chatbot")
st.caption("Simple AI-powered study assistant")

# ---------------------------
# Session State
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful study assistant."}
    ]

# ---------------------------
# Display Chat History
# ---------------------------
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )

    bot_reply = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )
