import streamlit as st
import time
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from safety import is_safe
from evaluation import evaluate_response
from logger import log_interaction

# ---------------------------
# Load Environment
# ---------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="🤖 Responsible AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
.stApp{
    background-color:#FF007Fs;
}
h1{
    color:#ffffff;
}
.stButton>button{
    width:100%;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙ Settings")

    MODEL = st.selectbox(
        "AI Model",
        [
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.3-70b-instruct",
            "deepseek/deepseek-chat"
        ]
    )

    temperature = st.slider("Creativity",0.0,1.0,0.7)
    max_tokens = st.slider("Max Tokens",100,1000,300)

    if st.button("🗑 Clear Chat"):
        st.session_state.history=[]
        st.session_state.messages=[]
        st.rerun()

# ---------------------------
# Session State
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history=[]

if "messages" not in st.session_state:
    st.session_state.messages=[]

# ---------------------------
# Title
# ---------------------------
st.title("🤖 Responsible AI Chatbot")
st.caption("Safe • Evaluated • Logged")

# ---------------------------
# Display Chat
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat Input
# ---------------------------
prompt = st.chat_input("Ask anything...")

# ---------------------------
# AI Function
# ---------------------------
def ask_ai():

    messages=[
        {
            "role":"system",
            "content":"You are a helpful, safe and responsible AI assistant."
        }
    ]

    for m in st.session_state.messages:
        messages.append(m)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------
# Generate Response
# ---------------------------
if prompt:

    st.session_state.messages.append(
        {"role":"user","content":prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if not is_safe(prompt):

        answer = "⚠ Sorry, I can't assist with harmful or unsafe requests."

        quality="Unsafe Prompt"

        elapsed=0

    else:

        start=time.time()

        try:
            with st.spinner("Thinking..."):
                answer=ask_ai()

        except Exception as e:
            answer=f"❌ API Error:\n{e}"

        elapsed=time.time()-start

        quality=evaluate_response(answer)

    st.session_state.messages.append(
        {"role":"assistant","content":answer}
    )

    st.session_state.history.append(
        (prompt,answer,quality,elapsed)
    )

    log_interaction(prompt,answer,quality,elapsed)

    with st.chat_message("assistant"):
        st.markdown(answer)

# ---------------------------
# Statistics
# ---------------------------
st.divider()

c1,c2,c3,c4=st.columns(4)

c1.metric("Questions",len(st.session_state.history))

if st.session_state.history:
    avg=sum(x[3] for x in st.session_state.history)/len(st.session_state.history)
else:
    avg=0

c2.metric("Average Time",f"{avg:.2f}s")

c3.metric("Model",MODEL.split("/")[-1])

c4.metric("Messages",len(st.session_state.messages))

# ---------------------------
# Download History
# ---------------------------
if st.session_state.history:

    df=pd.DataFrame(
        st.session_state.history,
        columns=["Question","Answer","Quality","Time"]
    )

    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        file_name="chat_history.csv",
        mime="text/csv"
    )

    text=""

    for q,a,_,_ in st.session_state.history:
        text+=f"User: {q}\nAI: {a}\n\n"

    st.download_button(
        "📄 Download TXT",
        text,
        file_name="chat_history.txt"
    )