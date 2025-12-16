import streamlit as st
import os
from openai import OpenAI
from PyPDF2 import PdfReader
import speech_recognition as sr
from st_audiorec import st_audiorec
import tempfile

# ---------------------------
# OpenAI Client (SAFE)
# ---------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Study Chatbot", layout="centered")
st.title("AI Study Chatbot")
st.caption("Text • Voice • Notes • PDFs")

# ---------------------------
# Language Selection
# ---------------------------
language = st.selectbox("Select Language", ["English", "Hindi"])

system_prompt = (
    "You are a helpful study assistant."
    if language == "English"
    else "You are a helpful study assistant. Reply in Hindi."
)

# ---------------------------
# Session State
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

if "context" not in st.session_state:
    st.session_state.context = ""

# ---------------------------
# File Upload Section
# ---------------------------
uploaded_file = st.file_uploader(
    "Upload notes (PDF / TXT) or image (optional)",
    type=["pdf", "txt", "png", "jpg", "jpeg"]
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        st.session_state.context = text
        st.success("PDF uploaded successfully. Ask questions from it.")

    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        st.session_state.context = text
        st.success("Notes uploaded successfully. Ask questions.")

    else:
        st.image(uploaded_file, caption="Uploaded Image")
        st.info("Image uploaded. Describe it in text to ask questions.")

# ---------------------------
# 🎤 Voice Input (Mic)
# ---------------------------
st.subheader("🎤 Voice Input")

audio_bytes = st_audiorec()
voice_text = ""

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        voice_text = recognizer.recognize_google(audio)
        st.success(f"Recognized text: {voice_text}")
    except:
        st.warning("Could not recognize voice. Please try again.")

# ---------------------------
# Display Chat History
# ---------------------------
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Type your question here...")

if voice_text:
    user_input = voice_text

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    messages = [{"role": "system", "content": system_prompt}]

    if st.session_state.context:
        messages.append(
            {
                "role": "system",
                "content": "Use the following notes to answer:\n" + st.session_state.context
            }
        )

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    bot_reply = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )

# ---------------------------
# Download Chat History
# ---------------------------
st.divider()
st.subheader("⬇️ Download Chat History")

history_text = ""
for msg in st.session_state.messages[1:]:
    history_text += f"{msg['role'].upper()}: {msg['content']}\n\n"

st.download_button(
    label="Download Chat History",
    data=history_text,
    file_name="chat_history.txt",
    mime="text/plain"
)
