import streamlit as st 
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3")
result = model.invoke(input="hellow world")
print(result)