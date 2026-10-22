import io
import json
from tempfile import NamedTemporaryFile
import PyPDF2
import requests
import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader  # Updated for PyPDF2 v3.0.0+

url = 'http://host.docker.internal:11434/api/chat'  # Updated to default Ollama API endpoint

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        try:
            text += page.extract_text()
        except:
            text+=''
    return text

def generate_chat(user_input, documentation=''):
    model = 'llama3.2:3b'

    system_prompt = (
        "Your name is Jeffrey. Answer the user's questions using your own "
        "knowledge and the document provided below. If the answer is in the "
        "document, base your answer on it."
    )
    if documentation:
        system_prompt += f"\n\n--- DOCUMENT START ---\n{documentation[:8000]}\n--- DOCUMENT END ---"

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input},
        ],
        'stream': True,
        'options': {'num_ctx': 4096},
    }

    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        full_response = ""
        message_placeholder = st.empty()

        for chunk in response.iter_lines():
            if chunk:
                try:
                    chunk_json = json.loads(chunk.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
                content = chunk_json.get('message', {}).get('content', '')
                full_response += content
                message_placeholder.markdown(full_response)

        return full_response
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {str(e)}"

      
st.set_page_config(page_title='Jeffrey Chat')
st.title('Chatting with Jeffrey.AI')
uploaded_files = st.file_uploader(label='Upload Documents for questioning:', 
                                type=['pdf'], 
                                accept_multiple_files=False)

documentation = ""
if uploaded_files:
    # Extract text from PDF
    documentation = extract_text_from_pdf(uploaded_files)
    st.success("PDF uploaded and processed successfully!")
    # Optional: show a preview of the extracted text
    with st.expander("View extracted PDF content"):
        st.text(documentation[:1000] + "...")  # Show first 1000 chars

# Using a form for chat input
with st.form("JeffreyChat"):
    user_input = st.text_input("Ask Jeffrey")
    submit_button = st.form_submit_button('Ask Jeffrey')
    
    if submit_button and user_input:
        with st.spinner('Jeffrey is thinking...'):
            response = generate_chat(user_input, documentation=documentation)
            st.divider()
            st.write("Complete response:")
            st.write(response)