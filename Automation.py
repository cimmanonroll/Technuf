import streamlit as st
import fitz  # PyMuPDF
import spacy
from langchain_community.llms import Ollama
import tempfile
import re
 
nlp = spacy.load("en_core_web_sm")
 
llm = Ollama(model="llama3")
 
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
 
def extract_relevant_sections(text):
    pattern = re.compile(r'^(.*?)(Scope of Work.*?)(Skills/Experience.*?)(Additionally, to be successful.*?)(?=\n[A-Z]|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(text)
    if match:
        before_scope_of_work = match.group(1).strip()
        scope_of_work = match.group(2).strip()
        skills_experience = match.group(3).strip()
        additionally_successful = match.group(4).strip()
        return before_scope_of_work + "\n\n" + scope_of_work + "\n\n" + skills_experience + "\n\n" + additionally_successful
    return ""
 
 
def generate_job_description(text):
    prompt = f"""
    Generate a job posting for Technuf LLC based in Maryland, USA. Use the information from the following text to create the job description using the template below:
   
    What we’re looking for [Do not change this header]:
    [Insert a one paragraph description of the name of the job that Technuf is looking for and what the job entails (make sure to start the paragraph with: Technuf is looking for...)]
   
    Responsibilities [Do not change this header]:
    [This section should copy everything from the Scope of Work section, in bullet points]
   
    Skills and Experience [Do not change this header]:
    [This section should copy everything from the Skills/Experience or Minimum Qualifications, Education and Experience section, in bullet points]
   
    Good to Have [Do not change this header]:
    [This section should copy everything from the Additionally, to be successful section]
   
    Education [Do not change this header]:
    Required: [insert required level of education here]
    Preferred: [insert preferred level of education here]
   
    Benefits [Do not change this header]:
    We offer a competitive pay and benefits package that includes generous paid-time-off including holidays, short-and-long-term disability; group health insurance including medical, dental and vision coverage, training and 401(k) retirement plan.
   
    Technuf is an Equal Opportunity/Affirmative Action Employer. Members of ethnic minorities, women, special disabled veterans, veterans of the Vietnam-era, recently separated veterans, and other protected veterans, persons of disability and/or persons age 40 and over are encouraged to apply.
   
    Ensure to exclude any mention of Evaluation Criteria, How to Apply, Note, and Interview Criteria.
 
    Use the information from the text below to fill in the relevant sections:
   
    {text}
    """
   
    response = llm.invoke(prompt)
    return response
 
# IMPORTANT
def clean_generated_text(text):
    cleaned_text = "\n".join([line for line in text.split("\n") if not line.strip().startswith("Here is")])
    return cleaned_text
 
def main():
    st.title("Technuf Automation")
    st.write("Upload a PDF file")
 
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
 
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_filepath = temp_file.name
 
        pdf_text = extract_text_from_pdf(temp_filepath)
        relevant_sections = extract_relevant_sections(pdf_text)
 
        if relevant_sections:
            st.subheader("Extracted Relevant Sections")
            st.write(relevant_sections)
            if st.button("Generate Job Description"):
                with st.spinner('Generating job posting'):
                    job_posting = get_job_title(relevant_sections) + "\n\n" + "Who we are \n Technuf, LLC is a Maryland based SBA certified 8(a) small business company providing leading-edge and proven technologies, industry vertical domain expertise and highly skilled and motivated professionals to achieve our customers mission critical business needs.\n\n"
                    job_description = generate_job_description(relevant_sections)
                    cleaned_job_description = clean_generated_text(job_description)
                    job_posting += cleaned_job_description
                    job_posting += "\n\nBenefits:\nWe offer a competitive pay and benefits package that includes generous paid-time-off including holidays, short-and-long-term disability; group health insurance including medical, dental and vision coverage, training and 401(k) retirement plan. \n"
                    job_posting += "\nTechnuf is an Equal Opportunity/Affirmative Action Employer. Members of ethnic minorities, women, special disabled veterans, veterans of the Vietnam-era, recently separated veterans, and other protected veterans, persons of disability and/or persons age 40 and over are encouraged to apply.\n"
                    st.subheader("Generated Job Description")
                    st.write(job_posting)
        else:
            st.error("No relevant sections found in the uploaded PDF.")
 
if __name__ == "__main__":
    main()
