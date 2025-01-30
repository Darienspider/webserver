import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from PyPDF2 import PdfReader  # To extract text from PDF
from gtts import gTTS #text to speech from google
import os
import datetime

# Define the prompt template
template = """
Answer the question below based on the documentation provided.

Documentation: {documentFeed}

Question: {question}

Answer: 
"""

# Initialize the model and the prompt
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template=template)
chain = prompt | model

def text_to_speech(text,language ="en", filename = 'none',slow=False):
    # variable that sets the voice type:  https://gtts.readthedocs.io/en/latest/module.html#localized-accents

    voice = 'us'
    filepath = f'ai_voice_output/{filename}'
    with open(f'{filepath}.txt','w') as f:
        f.write(text)
        f.close()
    
    tts = gTTS(text=text, lang=language,tld =voice)
    audio_file = f'{filepath}.mp3'
    tts.save(audio_file)
    return audio_file

# Function to extract text from the uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to handle questions
def answer_question(document_feed, question_text):
    response = chain.invoke({
        "documentFeed": document_feed,
        "question": question_text
    })
    return response

# Streamlit UI
st.title("AI Chat Bot with PDF Support")
st.write('Upload a PDF and ask questions about its content.')
audio_files = [i for i in os.listdir('ai_voice_output') if i.endswith('.mp3')]
audio_files.sort()
add_selectbox = st.sidebar.selectbox(
    "Previous Responses (Audio)",
    ['None'] +audio_files,
    key='AudioFile'
)
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

chosen_audio = st.session_state['AudioFile']
if chosen_audio != 'None':
    script = (str(chosen_audio).replace('mp3','txt'))
    with open(f'ai_voice_output/{script}','r') as f:
        text = f.read()
        st.write('Previous Response:')
        st.write(text)
        f.close()
    st.audio(f'ai_voice_output/{chosen_audio}',autoplay=True)


if uploaded_file:
    timestamp = str(datetime.datetime.now())
    # Extract text from the uploaded PDF
    document_feed = extract_text_from_pdf(uploaded_file)
    st.write("PDF content loaded successfully. You can now ask questions.")
    
    # Input for user question
    question_text = st.text_input("Ask a question about the PDF content:")
    if question_text:
        with st.spinner("Processing your question..."):
            answer = answer_question(document_feed, question_text)
        st.write("Answer:")
        st.write(answer)
        ai_voice_file = text_to_speech(answer, filename = timestamp,)
        st.audio(ai_voice_file,autoplay=True)
