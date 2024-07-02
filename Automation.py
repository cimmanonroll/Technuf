import streamlit as st
import fitz  # PyMuPDF
import spacy
import requests
from langchain_community.llms import Ollama
import tempfile


nlp = spacy.load("en_core_web_sm")

llm = Ollama(model="llama3")

# Gets the job title from the text
def get_job_title(text):
    doc = nlp(text)
    job_title = []
    capture = False
    for sent in doc.sents:
        if "title" in sent.text.lower():
            capture = True
       
        if capture:
            job_title = sent.text.strip()
            break
    job_title = job_title.split("\n")
    index = job_title.index("Task Order Title: ")
    return job_title[index + 1]

def extract_text_from_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

#changes NEEDED
def generate_job_description(text): 
    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are hiring recruiter at Technuf LLC who specializes in creating a clear and concise job description based on a solicitations document<|eot_id|>"
    prompt += "<|start_header_id|>user<|end_header_id|>\nBased on the document given, generate a fully filled out job requirements document that follows the following template exactly. Do not include anything that is not required by the template.\n"
    prompt += "What were looking for\n [Insert a one paragraph description of the name of the job that Technuf is looking for and what the job entails (make sure to start the paragraph with: Technuf is looking for...)]\n"
    prompt += "Responsibilities: \n [Insert responsibilities from the scope of work section here]\n"
    prompt += "Skills and Experience: \n [Insert needed skills and years of experience from the experience section here]\n"
    prompt += "Good to Have: \n [Insert skills from the \"Additionally, to be successful\" section here]\n"
    prompt += "Education: \n "
    prompt += "Required: [insert required level of education here] \n "
    prompt += "Preferred: [insert preferred level of education here]\n"
    prompt += f"""
    Generate a job posting for Technuf LLC based in Maryland, USA. Use the information from the following text to create the job description using the template above:

    {text}

    """
    url = "http://localhost:11434"  # URL of the Ollama server

    try:
        response = requests.post(url, json={"prompt": prompt})
        response.raise_for_status()  # Check for HTTP errors
        return response.json()["generated_text"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating job description: {e}")
        return None
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
            if st.button("Generate Job Description"):
                with st.spinner('Generating job posting'):
                    job_posting = get_job_title(pdf_text) + "\n\n" + "Who we are \n Technuf, LLC is a Maryland based SBA certified 8(a) small business company providing leading-edge and proven technologies, industry vertical domain expertise and highly skilled and motivated professionals to achieve our customers mission critical business needs.\n\n"
                    job_description = generate_job_description(pdf_text)
                    index_of_newline = job_description.rfind('\n')
                    st.subheader("Generated Job Description")
                    
                    if "Preferred:" not in job_description[index_of_newline:]:
                        job_description = job_description[:index_of_newline]
                    job_posting += job_description
                    job_posting += "\n\nBenefits:\nWe offer a competitive pay and benefits package that includes generous paid-time-off including holidays, short-and-long-term disability; group health insurance including medical, dental and vision coverage, training and 401(k) retirement plan. \n"
                    job_posting += "\nTechnuf is an Equal Opportunity/Affirmative Action Employer. Members of ethnic minorities, women, special disabled veterans, veterans of the Vietnam-era, recently separated veterans, and other protected veterans, persons of disability and/or persons age 40 and over are encouraged to apply.\n"
                    st.write(job_posting)
        else:
            st.error("No text found in the uploaded PDF.")

if __name__ == "__main__":
    main()
