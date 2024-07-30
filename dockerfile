# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /technufbot

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spacy models
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "technubot.py"]
