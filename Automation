import streamlit as st
import fitz  # PyMuPDF
import spacy
from langchain_community.llms import Ollama
import tempfile


nlp = spacy.load("en_core_web_sm")

llm = Ollama(model="llama3")

def extract_text_from_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

#changes NEEDED
def generate_job_description(text):
    prompt = f"""
    Generate a job posting for Technuf LLC based in Maryland, USA. Use the information from the following text to create the job description:

    {text}

    """
    response = llm.generate(prompts=[prompt])
    return response.generations[0][0]
#changes NEEDED

def main():
    st.title("Technuf Automation")
    st.write("Upload a PDF file")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_filepath = temp_file.name

        pdf_text = extract_text_from_pdf(temp_filepath)

        if pdf_text:
            st.subheader("Extracted Text")
            st.write(pdf_text)

            job_description = generate_job_description(pdf_text)
            st.subheader("Generated Job Description")
            st.write(job_description)
        else:
            st.error("No text found in the uploaded PDF.")

if __name__ == "__main__":
    main()
